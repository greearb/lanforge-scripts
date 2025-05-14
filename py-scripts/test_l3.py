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

        # Interopt example Creating stations
            Interopt testing creating stations
            ./test_l3.py --lfmgr 192.168.50.104\
             --test_duration 60s\
            --polling_interval 5s\
            --upstream_port 1.1.eth2\
            --radio radio==wiphy1,stations==2,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable\
            --endp_type lf_udp,lf_tcp,mc_udp\
            --rates_are_totals\
            --side_a_min_bps=2000000\
            --side_b_min_bps=3000000\
            --test_rig CT-ID-004\
            --test_tag test_l3\
            --dut_model_num AXE11000\
            --dut_sw_version 3.0.0.4.386_44266\
            --dut_hw_version 1.0\
            --dut_serial_num 123456\
            --tos BX,BE,VI,VO\
            --log_level info\
            --no_cleanup\
            --cleanup_cx


        # Interopt using existing stations
            Interopt testing creating stations
            ./test_l3.py --lfmgr 192.168.91.50\
             --test_duration 60s\
            --polling_interval 5s\
            --upstream_port 1.50.eth2\
            --endp_type lf_udp,lf_tcp,mc_udp\
            --rates_are_totals\
            --side_a_min_bps=2000000\
            --side_b_min_bps=3000000\
            --test_rig CT-ID-004\
            --test_tag test_l3\
            --dut_model_num AXE11000\
            --dut_sw_version 3.0.0.4.386_44266\
            --dut_hw_version 1.0\
            --dut_serial_num 123456\
            --tos BX,BE,VI,VO\
            --use_existing_station_list\
            --existing_station_list 1.83.en1,1.84.en1\
            --log_level info\
            --no_cleanup\
            --cleanup_cx

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
             --radio 'radio==1.1.wiphy0,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy1,stations==1,ssid==Netgear5g,ssid_pw==lanforge,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy2,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000\
             --test_rig ID_003 --test_tag 'l3_longevity' --dut_model_num GT-AXE11000 --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0 --dut_serial_num 12345678 --log_level debug

         # Setting wifi_settings per radio
            ./test_l3.py
            --lfmgr 192.168.100.116
            --local_lf_report_dir /home/lanforge/html-reports/
            --test_duration 15s
            --polling_interval 5s
            --upstream_port eth2
            --radio "radio==wiphy1,stations==4,ssid==asus11ax-5,ssid_pw==hello123,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down&&ht160_enable)"
            --endp_type lf_udp
            --rates_are_totals
            --side_a_min_bps=20000
            --side_b_min_bps=300000000
            --test_rig CT-US-001
            --test_tag 'test_l3'

         # Example : LAN-1927  WPA2-TLS-Configuration
            ./test_l3.py\
             --lfmgr 192.168.50.104\
             --test_duration 20s\
             --polling_interval 5s\
             --upstream_port 1.1.eth2\
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==lf_ax88u_5g,security==wpa2\
,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,\
wifi_extra==key_mgmt&&WPA-EAP!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!\
ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Disabled'\
             --endp_type lf_udp\
             --rates_are_totals\
             --side_a_min_bps=256000\
             --side_b_min_bps=300000000\
             --test_rig ID_003\
             --test_tag 'test_l3'\
             --dut_model_num GT-AXE11000\
             --dut_sw_version 3.0.0.4.386_44266\
             --dut_hw_version 1.0\
             --dut_serial_num 12345678\
             --log_level debug

        # Example : LAN-1927  WPA2-TTLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Disabled'
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
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Required'
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
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Required'
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
    Input       : Enum Val  : for list ,  telnet <mgr> 4001  , help add_profile

    Wifi_Mode
    <pre options='wifi_mode'>
    AUTO        |  0        #  Best Available
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
    abgn7       | 16        #  802.11abgn-EHT
                            #     a/b/g/n/AC/AX/EHT (dual-band AX) support
    bgn7        | 17        #  802.11bgn-EHT
    an7         | 18        #  802.11an-EHT
    a7          | 19        #  802.11a-EHT (6E disables /n and /ac)


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
from pprint import pformat
import logging
import platform
import itertools
import pandas as pd
# import traceback # TODO incorporate traceback if using try except
import json
import shutil

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

# LANforge automation-specific imports
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
lf_attenuator = importlib.import_module("py-scripts.lf_atten_mod_test")
modify_vap = importlib.import_module("py-scripts.modify_vap")
lf_modify_radio = importlib.import_module("py-scripts.lf_modify_radio")
lf_cleanup = importlib.import_module("py-scripts.lf_cleanup")
Realm = realm.Realm

logger = logging.getLogger(__name__)


class L3VariableTime(Realm):
    """Test class for variable-time Layer-3 traffic tests.

    This test class provides methods to run the configured test,
    query data for relevant LANforge ports and traffic pairs during
    the test, and generate reports upon completion.
    """
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
                 exit_on_ip_acquired=False,
                 csv_data_to_report=False,

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
                 ap_band_list=None,

                 #  for webgui
                 dowebgui=False,
                 test_name="",
                 ip="",
                 # for uniformity from webGUI result_dir as variable is used insead of local_lf_report_dir
                 result_dir="",
                 # wifi extra configuration
                 key_mgmt_list=None,
                 pairwise_list=None,
                 group_list=None,
                 psk_list=None,
                 wep_key_list=None,
                 ca_cert_list=None,
                 eap_list=None,
                 identity_list=None,
                 anonymous_identity_list=None,
                 phase1_list=None,
                 phase2_list=None,
                 passwd_list=None,
                 pin_list=None,
                 pac_file_list=None,
                 private_key_list=None,
                 pk_password_list=None,
                 hessid_list=None,
                 realm_list=None,
                 client_cert_list=None,
                 imsi_list=None,
                 milenage_list=None,
                 domain_list=None,
                 roaming_consortium_list=None,
                 venue_group_list=None,
                 network_type_list=None,
                 ipaddr_type_avail_list=None,
                 network_auth_type_list=None,
                 anqp_3gpp_cell_net_list=None,
                 ieee80211w_list=None,
                 interopt_mode=False
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
        self.interopt_mode = interopt_mode
        self.csv_data_to_report = csv_data_to_report
        self.kpi_csv = kpi_csv
        self.tos = tos.split(",")
        self.endp_types = endp_types.split(",")
        self.side_b = side_b
        self.side_a = side_a
        self.dowebgui = dowebgui
        self.test_name = test_name
        self.ip = ip
        self.result_dir = result_dir
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
        self.polling_interval = polling_interval
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

        # This is set after the 'build()' function is called, as the station
        # names in newly-created station profiles (i.e. not existing) are only
        # set *after creation*
        self.station_names_list = []

        self.wait_for_ip_sec = self.duration_time_to_seconds(wait_for_ip_sec)
        self.exit_on_ip_acquired = exit_on_ip_acquired

        self.attenuators = attenuators
        self.atten_vals = atten_vals
        if ((len(self.atten_vals) > 0) and (
                self.atten_vals[0] != -1) and (len(self.attenuators) == 0)):
            logger.error(
                "ERROR:  Attenuation values configured, but no Attenuator EIDs specified.\n")
            raise ValueError("Attenuation values configured, but no Attenuator EIDs specified.")

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
        self.resource_data = {}

        # endp data BK -A
        self.bk_clients_A = []
        self.bk_tos_ul_A = []
        self.bk_tos_dl_A = []
        self.bk_endp_eid_A = []

        # port data BK -A
        self.bk_port_eid_A = []
        self.bk_port_mac_A = []
        self.bk_port_ssid_A = []
        self.bk_port_channel_A = []
        self.bk_port_mode_A = []
        self.bk_port_observed_rx_rate_A = []
        self.bk_port_observed_tx_rate_A = []
        self.bk_port_traffic_type_A = []
        self.bk_port_protocol_A = []
        self.bk_port_offered_rx_rate_A = []
        self.bk_port_offered_tx_rate_A = []
        self.bk_rx_drop_percent_A = []

        # resource data BK -A
        self.bk_resource_host_A = []
        self.bk_resource_hw_ver_A = []
        self.bk_resource_eid_A = []
        self.bk_resource_kernel_A = []
        self.bk_resource_kernel_A = []
        self.bk_resource_alias_A = []

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
        self.bk_port_ssid_B = []
        self.bk_port_channel_B = []
        self.bk_port_mode_B = []
        self.bk_port_observed_rx_rate_B = []
        self.bk_port_observed_tx_rate_B = []
        self.bk_port_traffic_type_B = []
        self.bk_port_protocol_B = []
        self.bk_port_offered_rx_rate_B = []
        self.bk_port_offered_tx_rate_B = []
        self.bk_rx_drop_percent_B = []

        # resource data BK -B
        self.bk_resource_host_B = []
        self.bk_resource_hw_ver_B = []
        self.bk_resource_eid_B = []
        self.bk_resource_kernel_B = []
        self.bk_resource_kernel_B = []
        self.bk_resource_alias_B = []

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
        self.be_port_eid_A = []
        self.be_port_mac_A = []
        self.be_port_ssid_A = []
        self.be_port_channel_A = []
        self.be_port_mode_A = []
        self.be_port_observed_rx_rate_A = []
        self.be_port_observed_tx_rate_A = []
        self.be_port_traffic_type_A = []
        self.be_port_protocol_A = []
        self.be_port_offered_rx_rate_A = []
        self.be_port_offered_tx_rate_A = []
        self.be_rx_drop_percent_A = []

        # resource data BE -A
        self.be_resource_host_A = []
        self.be_resource_hw_ver_A = []
        self.be_resource_eid_A = []
        self.be_resource_kernel_A = []
        self.be_resource_kernel_A = []
        self.be_resource_alias_A = []

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
        self.be_port_eid_B = []
        self.be_port_mac_B = []
        self.be_port_channel_B = []
        self.be_port_ssid_B = []
        self.be_port_mode_B = []
        self.be_port_observed_rx_rate_B = []
        self.be_port_observed_tx_rate_B = []
        self.be_port_traffic_type_B = []
        self.be_port_protocol_B = []
        self.be_port_offered_rx_rate_B = []
        self.be_port_offered_tx_rate_B = []
        self.be_rx_drop_percent_B = []

        # resource data BE -B
        self.be_resource_host_B = []
        self.be_resource_hw_ver_B = []
        self.be_resource_eid_B = []
        self.be_resource_kernel_B = []
        self.be_resource_kernel_B = []
        self.be_resource_alias_B = []

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
        self.vi_port_eid_A = []
        self.vi_port_mac_A = []
        self.vi_port_ssid_A = []
        self.vi_port_channel_A = []
        self.vi_port_mode_A = []
        self.vi_port_observed_rx_rate_A = []
        self.vi_port_observed_tx_rate_A = []
        self.vi_port_traffic_type_A = []
        self.vi_port_protocol_A = []
        self.vi_port_offered_rx_rate_A = []
        self.vi_port_offered_tx_rate_A = []
        self.vi_rx_drop_percent_A = []

        # resource data VI -A
        self.vi_resource_host_A = []
        self.vi_resource_hw_ver_A = []
        self.vi_resource_eid_A = []
        self.vi_resource_kernel_A = []
        self.vi_resource_kernel_A = []
        self.vi_resource_alias_A = []

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
        self.vi_port_eid_B = []
        self.vi_port_mac_B = []
        self.vi_port_channel_B = []
        self.vi_port_ssid_B = []
        self.vi_port_mode_B = []
        self.vi_port_observed_rx_rate_B = []
        self.vi_port_observed_tx_rate_B = []
        self.vi_port_traffic_type_B = []
        self.vi_port_protocol_B = []
        self.vi_port_offered_rx_rate_B = []
        self.vi_port_offered_tx_rate_B = []
        self.vi_rx_drop_percent_B = []

        # resource data VI -B
        self.vi_resource_host_B = []
        self.vi_resource_hw_ver_B = []
        self.vi_resource_eid_B = []
        self.vi_resource_kernel_B = []
        self.vi_resource_kernel_B = []
        self.vi_resource_alias_B = []

        self.vi_request_dl_B = []
        self.vi_request_ul_B = []

        # dataframe  VI -B
        self.vi_dataframe_B = pd.DataFrame()

        # endp data VO -A
        self.vo_clients_A = []
        self.vo_tos_ul_A = []
        self.vo_tos_dl_A = []
        self.vo_endp_eid_A = []
        self.vo_port_mode_A = []
        self.vo_port_observed_rx_rate_A = []
        self.vo_port_observed_tx_rate_A = []
        self.vo_port_traffic_type_A = []
        self.vo_port_protocol_A = []
        self.vo_port_offered_rx_rate_A = []
        self.vo_port_offered_tx_rate_A = []

        # port data VO -A
        self.vo_port_eid_A = []
        self.vo_port_mac_A = []
        self.vo_port_channel_A = []
        self.vo_port_ssid_A = []
        self.vo_port_mode_A = []
        self.vo_port_observed_rx_rate_A = []
        self.vo_port_observed_tx_rate_A = []
        self.vo_port_traffic_type_A = []
        self.vo_port_protocol_A = []
        self.vo_port_offered_rx_rate_A = []
        self.vo_port_offered_tx_rate_A = []
        self.vo_rx_drop_percent_A = []

        # resource data VO -A
        self.vo_resource_host_A = []
        self.vo_resource_hw_ver_A = []
        self.vo_resource_eid_A = []
        self.vo_resource_kernel_A = []
        self.vo_resource_kernel_A = []
        self.vo_resource_alias_A = []

        self.vo_request_dl_A = []
        self.vo_request_ul_A = []

        # dataframe VO -A
        self.vo_dataframe_A = pd.DataFrame()

        # endp data VO -B
        self.vo_clients_B = []
        self.vo_tos_ul_B = []
        self.vo_tos_dl_B = []
        self.vo_endp_eid_dl_B = []

        # port data VO -B
        self.vo_port_eid_B = []
        self.vo_port_mac_B = []
        self.vo_port_channel_B = []
        self.vo_port_ssid_B = []
        self.vo_port_mode_B = []
        self.vo_port_observed_rx_rate_B = []
        self.vo_port_observed_tx_rate_B = []
        self.vo_port_traffic_type_B = []
        self.vo_port_protocol_B = []
        self.vo_port_offered_rx_rate_B = []
        self.vo_port_offered_tx_rate_B = []
        self.vo_rx_drop_percent_B = []

        # resource data VO -B
        self.vo_resource_host_B = []
        self.vo_resource_hw_ver_B = []
        self.vo_resource_eid_B = []
        self.vo_resource_kernel_B = []
        self.vo_resource_kernel_B = []
        self.vo_resource_alias_B = []

        self.vo_request_dl_B = []
        self.vo_request_ul_B = []

        # dataframe VO -B
        self.vo_dataframe_B = pd.DataFrame()

        self.client_dict_A = {}
        self.client_dict_B = {}

        # report object
        self.report = ''

        # dut information
        self.dut_model_num = 'Not Set'
        self.dut_hw_version = 'Not Set'
        self.dut_sw_version = 'Not Set'
        self.dut_serial_num = 'Not Set'

        # LANforge information
        self.lfmgr = self.lfclient_host
        self.lfmgr_port = self.lfclient_port
        self.upstream_port = self.side_b

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
        self.ap_band_list = ap_band_list if ap_band_list else ['2g', '5g', '6g']

        # wifi extra configuration
        self.key_mgmt_list = key_mgmt_list if key_mgmt_list else []
        self.pairwise_list = pairwise_list if pairwise_list else []
        self.group_list = group_list if group_list else []
        self.psk_list = psk_list if psk_list else []
        self.wep_key_list = wep_key_list if wep_key_list else []
        self.ca_cert_list = ca_cert_list if ca_cert_list else []
        self.eap_list = eap_list if eap_list else []
        self.identity_list = identity_list if identity_list else []
        self.anonymous_identity_list = anonymous_identity_list if anonymous_identity_list else []
        self.phase1_list = phase1_list if phase1_list else []
        self.phase2_list = phase2_list if phase2_list else []
        self.passwd_list = passwd_list if passwd_list else []
        self.pin_list = pin_list if pin_list else []
        self.pac_file_list = pac_file_list if pac_file_list else []
        self.private_key_list = private_key_list if private_key_list else []
        self.pk_password_list = pk_password_list if pk_password_list else []
        self.hessid_list = hessid_list if hessid_list else []
        self.realm_list = realm_list if realm_list else []
        self.client_cert_list = client_cert_list if client_cert_list else []
        self.imsi_list = imsi_list if imsi_list else []
        self.milenage_list = milenage_list if milenage_list else []
        self.domain_list = domain_list if domain_list else []
        self.roaming_consortium_list = roaming_consortium_list if roaming_consortium_list else []
        self.venue_group_list = venue_group_list if venue_group_list else []
        self.network_type_list = network_type_list if network_type_list else []
        self.ipaddr_type_avail_list = ipaddr_type_avail_list if ipaddr_type_avail_list else []
        self.network_auth_type_list = network_auth_type_list if network_auth_type_list else []
        self.anqp_3gpp_cell_net_list = anqp_3gpp_cell_net_list if anqp_3gpp_cell_net_list else []
        self.ieee80211w_list = ieee80211w_list if ieee80211w_list else []

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
            logger.debug("self.ap_read set to True and self.module is None, will set self.ap_read to False")
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
                    _radio_,
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
                station_profile = self.new_station_profile()
                station_profile.lfclient_url = self.lfclient_url
                station_profile.ssid = ssid_
                station_profile.ssid_pass = ssid_password_
                station_profile.security = ssid_security_
                station_profile.number_template = self.number_template
                station_profile.mode = mode_
                station_profile.desired_add_sta_flags = enable_flags_.copy()
                station_profile.desired_add_sta_flags_mask = enable_flags_.copy()

                # set_wifi_extra
                if key_mgmt_ != '[BLANK]':
                    station_profile.set_wifi_extra(key_mgmt=key_mgmt_,
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
                                                   anqp_3gpp_cell_net=anqp_3gpp_cell_net_)

                    # Configure protected management frames (PMF)
                    if ieee80211w_.lower() == 'disabled':
                        station_profile.set_command_param("add_sta", "ieee80211w", 0)
                    elif ieee80211w_.lower() == 'required':
                        station_profile.set_command_param("add_sta", "ieee80211w", 2)
                    else:
                        # may want to set an error if not optional yet for now default to optional
                        station_profile.set_command_param("add_sta", "ieee80211w", 1)

                # place the enable and disable flags
                # station_profile.desired_add_sta_flags = self.enable_flags
                # station_profile.desired_add_sta_flags_mask = self.enable_flags
                test_duration_sec = self.duration_time_to_seconds(self.test_duration)
                reset_port_min_time_sec = self.duration_time_to_seconds(reset_port_time_min_)
                reset_port_max_time_sec = self.duration_time_to_seconds(reset_port_time_max_)

                station_profile.set_reset_extra(reset_port_enable=reset_port_enable_,
                                                test_duration=test_duration_sec,
                                                reset_port_min_time=reset_port_min_time_sec,
                                                reset_port_max_time=reset_port_max_time_sec)
                self.station_profiles.append(station_profile)

            # Use existing station list is similiar to no rebuild
            if self.use_existing_station_lists:
                station_profile = self.new_station_profile()
                for existing_station_list in self.existing_station_lists:
                    station_profile.station_names.append(existing_station_list)

                self.station_profiles.append(station_profile)
        else:
            # Dataplane style test
            #
            # No need to create anything, as this assumes both test ports created,
            # rather than just 'side_b'
            self.station_names_list = [self.side_a]

        self.multicast_profile.host = self.lfclient_host
        self.cx_profile.host = self.lfclient_host
        self.cx_profile.port = self.lfclient_port
        self.cx_profile.name_prefix = self.name_prefix

        self.lf_endps = None
        self.udp_endps = None
        self.tcp_endps = None

    def _set_ports_up(self):
        """Set all test ports up.

        NOTE: This assumes the 'build()' function has successfully completed.
              Gathering station names requires the stations to have already been
              created, given the design of the StationProfile logic.
        """
        logger.info(f"Admin up upstream port and station port(s): {self.gather_port_eids()}")

        # Admin up upstream port
        self.admin_up(self.side_b)

        # Admin up created station port(s)
        #
        # NOTE: Could use common 'self.station_names_list' here,
        #       but there's benefit to up'ing and logging
        #       created vs. existing stations separately
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                logger.debug(f"Admin up station {sta}")
                self.admin_up(sta)

        # Admin up existing station port(s)
        if self.use_existing_station_lists:
            for existing_station in self.existing_station_lists:
                logger.debug(f"Bringing up existing stations {existing_station}")
                self.admin_up(existing_station)

    def _wait_ports_connected(self) -> int:
        """Check that all test ports connect to the DUT.

        Check includes phantom state, admin state, and IPv4 configured.

        NOTE: This assumes the 'build()' function has successfully completed.
              Gathering station names requires the stations to have already been
              created, given the design of the StationProfile logic.

        Returns:
            int: 0 on success, non-zero on failure
        """
        success = self.wait_for_ip([self.side_b] + self.station_names_list,
                                   timeout_sec=self.wait_for_ip_sec)
        if success:
            logger.info("All ports connected successfully")
            if self.exit_on_ip_acquired:
                logger.info("Configured to exit on successful IPv4 configuration")
                exit(1)
        elif self.interopt_mode:
            logger.warning("Running in InterOp mode, ignoring IPv4 configuration failure and continuing")
        else:
            logger.critical("One or more test ports did not receive an IPv4 address "
                            f"in {self.wait_for_ip_sec} seconds")

        return 0 if success else -1

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
        eid = self.name_to_eid(port_eid)
        if not self.dowebgui:
            logger.info("endp-stats-for-port, port-eid: {}".format(port_eid))
            logger.debug(
                "eid: {eid}".format(eid=eid))

        # Convert all eid elements to strings
        eid[0] = str(eid[0])
        eid[1] = str(eid[1])
        eid[2] = str(eid[2])

        for endp in endps:
            # pprint(endp)
            if not self.dowebgui:
                logging.info(pformat(endp))
            eid_endp = endp["eid"].split(".")
            logger.debug(
                "Comparing eid:{eid} to endp-id {eid_endp}".format(eid=eid, eid_endp=eid_endp))
            # Look through all the endpoints (endps), to find the port the port_eid is using.
            # The port_eid that has the same Shelf, Resource, and Port as the eid_endp (looking at all the endps)
            # Then read the eid_endp to get the delay, jitter and rx rate
            # Note: the endp eid is shelf.resource.port.endp-id, the eid can be treated somewhat as
            # child class of port-eid , and look up the port the eid is using.
            if eid[0] == eid_endp[0] and eid[1] == eid_endp[1] and eid[2] == eid_endp[2]:
                if ((endp['delay'] is str and not endp['delay'].isnumeric()) or endp['delay'] is None):
                    logging.debug(
                        'Expected integer response for delay, received non-numeric string instead. Replacing with 0')
                    lat += 0
                else:
                    lat += int(endp['delay'])

                if ((endp['jitter'] is str and not endp['jitter'].isnumeric()) or endp['jitter'] is None):
                    logging.debug(
                        'Expected integer response for jitter, received non-numeric string instead. Replacing with 0')
                    jit += 0
                else:
                    jit += int(endp["jitter"])
                # lat += int(endp["delay"])
                # jit += int(endp["jitter"])
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

                    if (isinstance(endp['rx rate'], str)
                            and not endp['rx rate'].isnumeric()) or endp['rx rate'] is None:
                        logging.debug(
                            'Expected integer response for rx rate, received non-numeric string instead. Replacing with 0')
                        total_dl_rate += 0
                    else:
                        total_dl_rate += int(endp["rx rate"])

                    if (isinstance(endp['rx rate ll'], str)
                            and not endp['rx rate ll'].isnumeric()) or endp['rx rate ll'] is None:
                        logging.debug(
                            'Expected integer response for rx rate ll, received non-numeric string instead. Replacing with 0')
                        total_dl_rate_ll += 0
                    else:
                        total_dl_rate_ll += int(endp["rx rate ll"])

                    if (isinstance(endp['rx pkts ll'], str)
                            and not endp['rx pkts ll'].isnumeric()) or endp['rx pkts ll'] is None:
                        logging.debug(
                            'Expected integer response for rx pkts ll, received non-numeric string instead. Replacing with 0')
                        total_dl_pkts_ll += 0
                    else:
                        total_dl_pkts_ll += int(endp["rx pkts ll"])

                    if (isinstance(endp['rx drop %'], str)
                            and not endp['rx drop %'].isnumeric()) or endp['rx drop %'] is None:
                        logging.debug(
                            'Expected integer response for rx drop %, received non-numeric string instead. Replacing with 0')
                        dl_rx_drop_percent = 0
                    else:
                        dl_rx_drop_percent = round(endp["rx drop %"], 2)

                # -B upload side
                else:
                    if (isinstance(endp['rx rate'], str)
                            and not endp['rx rate'].isnumeric()) or endp['rx rate'] is None:
                        logging.debug(
                            'Expected integer response for rx rate, received non-numeric string instead. Replacing with 0')
                        total_ul_rate += 0
                    else:
                        total_ul_rate += int(endp["rx rate"])

                    if (isinstance(endp['rx rate ll'], str)
                            and not endp['rx rate ll'].isnumeric()) or endp['rx rate ll'] is None:
                        logging.debug(
                            'Expected integer response for rx rate ll, received non-numeric string instead. Replacing with 0')
                        total_ul_rate_ll += 0
                    else:
                        total_ul_rate_ll += int(endp["rx rate ll"])

                    if (isinstance(endp['rx pkts ll'], str)
                            and not endp['rx pkts ll'].isnumeric()) or endp['rx pkts ll'] is None:
                        logging.debug(
                            'Expected integer response for rx pkts ll, received non-numeric string instead. Replacing with 0')
                        total_ul_pkts_ll += 0
                    else:
                        total_ul_pkts_ll += int(endp["rx pkts ll"])

                    if (isinstance(endp['rx drop %'], str)
                            and not endp['rx drop %'].isnumeric()) or endp['rx drop %'] is None:
                        logging.debug(
                            'Expected integer response for rx drop %, received non-numeric string instead. Replacing with 0')
                        ul_rx_drop_percent = 0
                    else:
                        ul_rx_drop_percent = round(endp["rx drop %"], 2)

                    # total_ul_rate += int(endp["rx rate"])
                    # total_ul_rate_ll += int(endp["rx rate ll"])
                    # total_ul_pkts_ll += int(endp["rx pkts ll"])
                    # ul_rx_drop_percent = round(endp["rx drop %"], 2)

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
        try:
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
                                if isinstance(value, str) and not value.isnumeric():
                                    logging.debug(
                                        'Expected integer response for rx rate, received non-numeric string instead. Replacing with 0')
                                    value = 0
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
        except Exception as e:
            overall_response = self.json_get('/cx/all/')
            logger.info(overall_response)
            logger.error(f"Endpoint not fetched from API {e}")
        # Unicast endpoints
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e
        try:
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
                                    if isinstance(value, str) and not value.isnumeric():
                                        logging.debug(
                                            'Expected integer response for rx rate, received non-numeric string instead. Replacing with 0')
                                        value = 0
                                    # This hack breaks for mcast or if someone names endpoints weirdly.
                                    # logger.info("item: ", item, " rx-bps: ", value_rx_bps)
                                    if item.endswith("-A"):
                                        total_dl += int(value)
                                    elif item.endswith("-B"):
                                        total_ul += int(value)
                                if value_name == 'rx rate ll':
                                    if isinstance(value, str) and not value.isnumeric():
                                        logging.debug(
                                            'Expected integer response for rx rate ll, received non-numeric string instead. Replacing with 0')
                                        value = 0
                                    # This hack breaks for mcast or if someone
                                    # names endpoints weirdly.
                                    if item.endswith("-A"):
                                        total_dl_ll += int(value)
                                    elif item.endswith("-B"):
                                        total_ul_ll += int(value)
        except Exception as e:
            overall_response = self.json_get('/cx/all/')
            logger.info(overall_response)
            logger.error(f"Endpoint not fetched from API {e}")
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
    # Time Constrains use for webGUI compatibility

    def get_time_stamp_local(self):
        return time.strftime('%Y-%m-%d-%H-%M-%S',
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

    def gather_port_eids(self) -> list:
        """Query test object for list of ports used in test.

        This includes the both the station(s) and the upstream.

        NOTE: This assumes the 'build()' function has successfully completed.
              Gathering station names requires the stations to have already been
              created, given the design of the StationProfile logic.
        """
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
            # TODO for multicast when using single station there needs to be an interop mode
            # with a single transmitter for all of the multi-cast
            logger.info("Creating test station port(s)")
            for station_profile in self.station_profiles:
                if not rebuild and not self.use_existing_station_lists:
                    station_profile.use_security(
                        station_profile.security,
                        station_profile.ssid,
                        station_profile.ssid_pass)
                    station_profile.set_number_template(
                        station_profile.number_template)
                    logger.debug(f"Creating station port(s) on radio {self.radio_name_list[index]}")

                    station_profile.create(
                        radio=self.radio_name_list[index],
                        sta_names_=self.station_lists[index],
                        debug=self.debug,
                        sleep_time=0)
                    index += 1

                self.station_count += len(station_profile.station_names)

                # Build/update connection types
                # TODO build multicast once for each endp type
                for etype in self.endp_types:
                    # TODO multi cast build each type only once
                    if etype == "mc_udp" or etype == "mc_udp6":
                        # TODO add multicast to name be passed in
                        for _tos in self.tos:
                            logger.info("Creating Multicast connections for endpoint type:  {etype} TOS: {tos}".format(
                                etype=etype, tos=_tos))
                            self.multicast_profile.create_mc_tx(
                                etype, self.side_b, tos=_tos, add_tos_to_name=True)
                            self.multicast_profile.create_mc_rx(
                                etype, side_rx=station_profile.station_names, tos=_tos, add_tos_to_name=True)

                # Multicast needs to have only one tx endpt, if only one profile needed
                for etype in self.endp_types:
                    if etype == "lf_udp" or etype == "lf_udp6" or etype == "lf_tcp" or etype == "lf_tcp6":
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

        # Generate list of all stations, both created and existing
        #
        # Both are stored in 'self.station_profiles', but only
        # the 'station_names' field is really valid for the existing
        # stations profile
        for station_profile in self.station_profiles:
            self.station_names_list.extend(station_profile.station_names)

        if self.dataplane:
            self._pass(
                "PASS: CX build finished: created/updated:  %s connections." %
                self.cx_count)
        else:
            self._pass(
                "PASS: Stations & CX build finished: created/updated: %s stations and %s connections." %
                (self.station_count, self.cx_count))

    def start(self, print_pass=False) -> int:
        """Run configured Layer-3 variable time test.

        Args:
            print_pass (bool, optional): Enable printing test pass upon completion.
                                         Defaults to False.

        Returns:
            int: 0 on success, non-zero on failure.
        """
        self._set_ports_up()
        self._wait_ports_connected()

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

                # Update connections with the new rate and pdu size config.
                self.build(rebuild=True)

                if self.ap_read:
                    for band in self.ap_band_list:
                        self.ap.clear_stats(band)

                for atten_val in self.atten_vals:
                    if atten_val != -1:
                        for _ in self.attenuators:
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
                    start_time = cur_time
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
                    self.overall = []

                    # Monitor loop
                    while cur_time < end_time:
                        # interval_time = cur_time + datetime.timedelta(seconds=5)
                        interval_time = cur_time + \
                            datetime.timedelta(
                                seconds=self.polling_interval_seconds)
                        # logger.info("polling_interval_seconds {}".format(self.polling_interval_seconds))

                        # Gather interop data

                        # Holds off for the interval and allows for port reset
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
                        # Added logic creating a csv file for webGUI to get runtime data
                        if self.dowebgui:
                            time_difference = abs(end_time - datetime.datetime.now())
                            total_hours = time_difference.total_seconds() / 3600
                            remaining_minutes = (total_hours % 1) * 60
                            remaining_time = [
                                str(int(total_hours)) + " hr and " + str(int(remaining_minutes)) + " min" if int(
                                    total_hours) != 0 or int(remaining_minutes) != 0 else '<1 min'][0]
                            total = 0
                            for k, v in endp_rx_map.items():
                                if 'MLT-' in k:
                                    total += v
                            self.overall.append(
                                {self.tos[0]: total, "timestamp": self.get_time_stamp_local(),
                                 "status": "Running",
                                 "start_time": start_time.strftime('%Y-%m-%d-%H-%M-%S'),
                                 "end_time": end_time.strftime('%Y-%m-%d-%H-%M-%S'), "remaining_time": remaining_time})
                            df1 = pd.DataFrame(self.overall)
                            df1.to_csv('{}/overall_multicast_throughput.csv'.format(self.result_dir), index=False)
                            with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.ip,
                                                                                                             self.test_name),
                                      'r') as file:
                                data = json.load(file)
                                if data["status"] != "Running":
                                    logging.warning('Test is stopped by the user')
                                    self.overall[len(self.overall) - 1]["end_time"] = self.get_time_stamp_local()
                                    break
                        if not self.dowebgui:
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
                                    if not self.dowebgui:
                                        # print("response".format(response))
                                        logger.info(pformat(response))
                                    port_data = response['interface']
                                    logger.info(
                                        "From LANforge: port_data, response['insterface']:{}".format(port_data))
                                    mac = port_data['mac']
                                    if not self.dowebgui:
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
                                    if not self.dowebgui:
                                        logger.info("mac {mac} ap_row_tx_dl {ap_row_tx_dl}".format(
                                            mac=mac, ap_row_tx_dl=ap_row_tx_dl))
                                    # Find latency, jitter for connections
                                    # using this port.
                                    (latency, jitter, total_dl_rate, total_dl_rate_ll, total_dl_pkts_ll,
                                     dl_rx_drop_percent, total_ul_rate, total_ul_rate_ll,
                                     total_ul_pkts_ll, ul_rx_drop_percent) = self.get_endp_stats_for_port(
                                        port_data["port"], endps)

                                    ap_row_tx_dl.append(ap_row_chanim)

                                    self.write_dl_port_csv(
                                        len(self.station_names_list),
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
                                    # latency, jitter, total_dl_rate, total_dl_rate_ll, total_dl_pkts_ll, dl_rx_drop_percent, total_ul_rate,
                                    # total_ul_rate_ll, total_ul_pkts_ll, ul_tx_drop_percent = self.get_endp_stats_for_port(
                                    #    port_data["port"], endps)
                                    self.write_ul_port_csv(
                                        len(self.station_names_list),
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
                                        ap_row_rx_ul)  # ap_ul_row added
                                if not self.dowebgui:
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
                                    logger.debug(pformat(response))
                                else:
                                    port_data = response['interface']
                                    (latency, jitter, total_dl_rate, total_dl_rate_ll,
                                     total_dl_pkts_ll, dl_rx_drop_percent, total_ul_rate,
                                     total_ul_rate_ll, total_ul_pkts_ll, ul_rx_drop_percent) = self.get_endp_stats_for_port(
                                        port_data["port"], endps)
                                    self.write_dl_port_csv(
                                        len(self.station_names_list),
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
                    # logger.info(pformat(all_dl_ports_stations_df))

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
                                                                                                     'Ul-Rx-Goodput-bps', 'Ul-Rx-Rate-ll', 'Ul-Rx-Pkts-ll',
                                                                                                     'Dl-Rx-Goodput-bps', 'Dl-Rx-Rate-ll', 'Dl-Rx-Pkts-ll']].sum()
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
                        all_dl_ports_stations_sum_df['Rx-Bps-Diff'] = all_dl_ports_stations_sum_df['Rx-Bps'].diff()
                        all_dl_ports_stations_sum_df['Tx-Bps-Diff'] = all_dl_ports_stations_sum_df['Tx-Bps'].diff()
                        all_dl_ports_stations_sum_df['Rx-Latency-Diff'] = all_dl_ports_stations_sum_df['Rx-Latency'].diff()
                        all_dl_ports_stations_sum_df['Rx-Jitter-Diff'] = all_dl_ports_stations_sum_df['Rx-Jitter'].diff()
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
                                                                                                         'Ul-Rx-Goodput-bps', 'Ul-Rx-Rate-ll', 'Ul-Rx-Pkts-ll',
                                                                                                         'Dl-Rx-Goodput-bps', 'Dl-Rx-Rate-ll', 'Dl-Rx-Pkts-ll']].sum()
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
                        len(self.station_names_list),
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
                        len(self.station_names_list),
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

        return 0

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

    def create_resource_alias(self, eid='NA', host='NA', hw_version='NA', kernel='NA'):
        if "Win" in hw_version:
            hardware = "Win"
        elif "Linux" in hw_version:
            hardware = "Linux"
        elif "Apple" in hw_version:
            if "iOS" in kernel:
                hardware = "iOS"
            else:
                hardware = "Apple"
        else:
            hardware = "Android"
        alias = eid + "_" + host + "_" + hardware

        return alias

    def evaluate_qos(self):
        # for port:
        # curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.104:8080/port/all | json_pp
        # curl --user "lanforge:lanforge" -H 'Accept: application/json'
        # http://192.168.0.103:8080/port/all?fields=alias,mac,channel,bps+rx,rx-rate,bps+tx,tx-rate
        # | json_pp

        # for endp
        # curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.104:8080/endp/all | json_pp
        # curl --user "lanforge:lanforge" -H 'Accept: application/json'
        # http://192.168.0.104:8080/endp/all?fields=name,tx+rate+ll,tx+rate,rx+rate+ll,rx+rate,a/b,tos
        # | json_pp

        # gather port data
        # TODO
        self.port_data = self.json_get('port/all?fields=alias,port,mac,channel,ssid,mode,bps+rx,rx-rate,bps+tx,tx-rate')
        # self.port_data = self.json_get('port/all')
        self.port_data.pop("handler")
        self.port_data.pop("uri")
        self.port_data.pop("warnings")
        logger.info("self.port_data type: {dtype} data: {data}".format(dtype=type(self.port_data), data=self.port_data))

        self.resource_data = self.json_get('resource/all?fields=eid,hostname,hw+version,kernel')
        # self.resource_data = self.json_get('resource/all')
        self.resource_data.pop("handler")
        self.resource_data.pop("uri")
        # self.resource_data.pop("warnings")
        if not self.dowebgui:
            logger.info("self.resource_data type: {dtype}".format(dtype=type(self.port_data)))
        # logger.info("self.resource_data : {data}".format(data=self.port_data))

        # This is to handle the case where there is only one resourse
        if "resource" in self.resource_data.keys():
            self.resource_data["resources"] = [{'1.1': self.resource_data['resource']}]
            self.resource_data.pop("resource")

        # Note will type will only work for 5.4.7
        # gather endp data
        endp_type_present = False

        # TODO check for 400 bad request instead of try except
        self.endp_data = self.json_get(
            'endp/all?fields=name,tx+rate+ll,tx+rate,rx+rate+ll,rx+rate,a/b,tos,eid,type,rx Drop %25')
        if self.endp_data is not None:
            endp_type_present = True
        else:
            logger.info(
                "Consider upgrading to 5.4.7 + endp field type not supported in LANforge GUI version results for Multicast reversed in graphs and tables")
            self.endp_data = self.json_get(
                'endp/all?fields=name,tx+rate+ll,tx+rate,rx+rate+ll,rx+rate,a/b,eid,rx Drop %25')
            endp_type_present = False
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
                key=endp_data_key, name=endp_data[endp_data_key]['name'], ab=endp_data[endp_data_key]['a/b'], rx_rate=endp_data[endp_data_key]['rx rate']))

            # Gather data for upload , download for the four data types BK, BE, VI, VO, place the
            # the data_set will be the upload and download rates for each client
            # the y_axis values are the clients
            # TODO how many data sets
            # for multicast upstream is A
            # for unicast the upstream is B

            # multi cast A side is upstream  Being explicite with code coudl have been done with arrays, yet wanted the code to be
            # maintainable
            if endp_type_present:
                # note for multicast there is no a side traffic
                if endp_data[endp_data_key]['type'] == 'Mcast':
                    if endp_data[endp_data_key]['tos'] == 'BK':
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.bk_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_A.append(client_alias)
                                    break

                            if resource_found is False:
                                self.bk_resource_host_A.append('NA')
                                self.bk_resource_hw_ver_A.append('NA')
                                self.bk_resource_eid_A.append('NA')
                                self.bk_resource_kernel_A.append('NA')
                                self.bk_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.bk_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.bk_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_offered_tx_rate_A.append('0')  # a side tx side_a_min_bps
                                    self.bk_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_A.append('NA')
                                self.bk_port_ssid_A.append('NA')
                                self.bk_port_mode_A.append('NA')
                                self.bk_port_traffic_type_A.append("NA")
                                self.bk_port_offered_rx_rate_A.append("NA")
                                self.bk_port_offered_tx_rate_A.append("NA")
                                self.bk_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.bk_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.bk_resource_host_B.append('NA')
                                self.bk_resource_hw_ver_B.append('NA')
                                self.bk_resource_eid_B.append('NA')
                                self.bk_resource_kernel_B.append('NA')
                                self.bk_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.bk_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.bk_port_offered_rx_rate_B.append('0')
                                    self.bk_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_B.append('NA')
                                self.bk_port_ssid_B.append('NA')
                                self.bk_port_mode_B.append('NA')
                                self.bk_port_traffic_type_B.append("NA")
                                self.bk_port_offered_rx_rate_B.append("NA")
                                self.bk_port_offered_tx_rate_B.append("NA")
                                self.bk_port_channel_B.append("NA")

                    elif endp_data[endp_data_key]['tos'] == 'BE':
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.be_clients_A.append(endp_data[endp_data_key]['name'])
                            self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.be_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.be_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.be_resource_host_A.append('NA')
                                self.be_resource_hw_ver_A.append('NA')
                                self.be_resource_eid_A.append('NA')
                                self.be_resource_kernel_A.append('NA')
                                self.be_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.be_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.be_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_offered_tx_rate_A.append('0')  # a side tx  side_a_min_bps
                                    self.be_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_A.append('NA')
                                self.be_port_ssid_A.append('NA')
                                self.be_port_mode_A.append('NA')
                                self.be_port_traffic_type_A.append("NA")
                                self.be_port_offered_rx_rate_A.append("NA")
                                self.be_port_offered_tx_rate_A.append("NA")
                                self.be_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.be_clients_B.append(endp_data[endp_data_key]['name'])
                            self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.be_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.be_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.be_resource_host_B.append('NA')
                                self.be_resource_hw_ver_B.append('NA')
                                self.be_resource_eid_B.append('NA')
                                self.be_resource_kernel_B.append('NA')
                                self.be_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.be_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.be_port_offered_rx_rate_B.append('0')
                                    self.be_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_B.append('NA')
                                self.be_port_ssid_B.append('NA')
                                self.be_port_mode_B.append('NA')
                                self.be_port_traffic_type_B.append("NA")
                                self.be_port_offered_rx_rate_B.append("NA")
                                self.be_port_offered_tx_rate_B.append("NA")
                                self.be_port_channel_B.append("NA")

                    elif endp_data[endp_data_key]['tos'] == 'VI':
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.vi_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_A.append('NA')
                                self.vi_resource_hw_ver_A.append('NA')
                                self.vi_resource_eid_A.append('NA')
                                self.vi_resource_kernel_A.append('NA')
                                self.vi_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vi_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.vi_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vi_port_offered_tx_rate_A.append('0')  # a side tx, side_a_min_bps
                                    self.vi_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_A.append('NA')
                                self.vi_port_ssid_A.append('NA')
                                self.vi_port_mode_A.append('NA')
                                self.vi_port_traffic_type_A.append("NA")
                                self.vi_port_offered_rx_rate_A.append("NA")
                                self.vi_port_offered_tx_rate_A.append("NA")
                                self.vi_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.vi_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_B.append('NA')
                                self.vi_resource_hw_ver_B.append('NA')
                                self.vi_resource_eid_B.append('NA')
                                self.vi_resource_kernel_B.append('NA')
                                self.vi_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vi_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    self.vi_port_offered_rx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    # (self.cx_profile.side_b_min_bps) # b side tx
                                    self.vi_port_offered_tx_rate_B.append('0')
                                    self.vi_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_B.append('NA')
                                self.vi_port_ssid_B.append('NA')
                                self.vi_port_mode_B.append('NA')
                                self.vi_port_traffic_type_B.append("NA")
                                self.vi_port_offered_rx_rate_B.append("NA")
                                self.vi_port_offered_tx_rate_B.append("NA")
                                self.vi_port_channel_B.append("NA")

                    elif endp_data[endp_data_key]['tos'] == 'VO':
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.vo_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vo_resource_host_A.append('NA')
                                self.vo_resource_hw_ver_A.append('NA')
                                self.vo_resource_eid_A.append('NA')
                                self.vo_resource_kernel_A.append('NA')
                                self.vo_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vo_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.vo_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_offered_tx_rate_A.append('0')  # a side tx  side_a_min_bps
                                    self.vo_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_A.append('NA')
                                self.vo_port_ssid_A.append('NA')
                                self.vo_port_mode_A.append('NA')
                                self.vo_port_traffic_type_A.append("NA")
                                self.vo_port_offered_rx_rate_A.append("NA")
                                self.vo_port_offered_tx_rate_A.append("NA")
                                self.vo_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.vo_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vo_resource_host_B.append('NA')
                                self.vo_resource_hw_ver_B.append('NA')
                                self.vo_resource_eid_B.append('NA')
                                self.vo_resource_kernel_B.append('NA')
                                self.vo_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vo_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.vo_port_offered_rx_rate_B.append('0')
                                    self.vo_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_B.append('NA')
                                self.vo_port_ssid_B.append('NA')
                                self.vo_port_mode_B.append('NA')
                                self.vo_port_traffic_type_B.append("NA")
                                self.vo_port_offered_rx_rate_B.append("NA")
                                self.vo_port_offered_tx_rate_B.append("NA")
                                self.vo_port_channel_B.append("NA")

                # for unicast the upstream is B and downstream is A
                # note for B tx is download and rx is uploat
                # TODO support  'LF'
                elif endp_data[endp_data_key]['type'] == 'LF/TCP' or endp_data[endp_data_key]['type'] == 'LF/UDP':
                    if endp_data[endp_data_key]['tos'] == 'BK':
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.bk_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_A.append(client_alias)

                            if resource_found is False:
                                self.bk_resource_host_A.append('NA')
                                self.bk_resource_hw_ver_A.append('NA')
                                self.bk_resource_eid_A.append('NA')
                                self.bk_resource_kernel_A.append('NA')
                                self.bk_resource_alias_A.append('NA')
                                break

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.bk_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.bk_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.bk_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_A.append('NA')
                                self.bk_port_ssid_A.append('NA')
                                self.bk_port_mode_A.append('NA')
                                self.bk_port_traffic_type_A.append("NA")
                                self.bk_port_offered_rx_rate_A.append("NA")
                                self.bk_port_offered_tx_rate_A.append("NA")
                                self.bk_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.bk_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.bk_resource_host_B.append('NA')
                                self.bk_resource_hw_ver_B.append('NA')
                                self.bk_resource_eid_B.append('NA')
                                self.bk_resource_kernel_B.append('NA')
                                self.bk_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.bk_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    self.bk_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.bk_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_B.append('NA')
                                self.bk_port_ssid_B.append('NA')
                                self.bk_port_mode_B.append('NA')
                                self.bk_port_traffic_type_B.append("NA")
                                self.bk_port_offered_rx_rate_B.append("NA")
                                self.bk_port_offered_tx_rate_B.append("NA")
                                self.bk_port_channel_B.append("NA")

                    # for unicast the upstream is B and downstream is A
                    elif endp_data[endp_data_key]['tos'] == 'BE':

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.be_clients_A.append(endp_data[endp_data_key]['name'])
                            self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.be_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.be_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.be_resource_host_A.append('NA')
                                self.be_resource_hw_ver_A.append('NA')
                                self.be_resource_eid_A.append('NA')
                                self.be_resource_kernel_A.append('NA')
                                self.be_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.be_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.be_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.be_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_A.append('NA')
                                self.be_port_ssid_A.append('NA')
                                self.be_port_mode_A.append('NA')
                                self.be_port_traffic_type_A.append("NA")
                                self.be_port_offered_rx_rate_A.append("NA")
                                self.be_port_offered_tx_rate_A.append("NA")
                                self.be_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.be_clients_B.append(endp_data[endp_data_key]['name'])
                            self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.be_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.be_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.be_resource_host_B.append('NA')
                                self.be_resource_hw_ver_B.append('NA')
                                self.be_resource_eid_B.append('NA')
                                self.be_resource_kernel_B.append('NA')
                                self.be_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.be_port_eid_B.append(eid_tmp_port)

                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    self.be_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.be_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_B.append('NA')
                                self.be_port_ssid_B.append('NA')
                                self.be_port_mode_B.append('NA')
                                self.be_port_traffic_type_B.append("NA")
                                self.be_port_offered_rx_rate_B.append("NA")
                                self.be_port_offered_tx_rate_B.append("NA")
                                self.be_port_channel_B.append("NA")

                    elif endp_data[endp_data_key]['tos'] == 'VI':
                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.vi_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_A.append('NA')
                                self.vi_resource_hw_ver_A.append('NA')
                                self.vi_resource_eid_A.append('NA')
                                self.vi_resource_kernel_A.append('NA')
                                self.vi_resource_alias_A.append(client_alias)

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vi_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.vi_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vi_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vi_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_A.append('NA')
                                self.vi_port_ssid_A.append('NA')
                                self.vi_port_mode_A.append('NA')
                                self.vi_port_traffic_type_A.append("NA")
                                self.vi_port_offered_rx_rate_A.append("NA")
                                self.vi_port_offered_tx_rate_A.append("NA")
                                self.vi_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.vi_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_B.append(client_alias)
                                    break

                            if resource_found is False:
                                self.vi_resource_host_B.append('NA')
                                self.vi_resource_hw_ver_B.append('NA')
                                self.vi_resource_eid_B.append('NA')
                                self.vi_resource_kernel_B.append('NA')
                                self.vi_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vi_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    self.vi_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vi_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vi_port_channel_B.append(port_data[port_data_key]["channel"])

                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_B.append('NA')
                                self.vi_port_ssid_B.append('NA')
                                self.vi_port_mode_B.append('NA')
                                self.vi_port_traffic_type_B.append("NA")
                                self.vi_port_offered_rx_rate_B.append("NA")
                                self.vi_port_offered_tx_rate_B.append("NA")
                                self.vi_port_channel_B.append("NA")

                    elif endp_data[endp_data_key]['tos'] == 'VO':
                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_port_protocol_A.append(endp_data[endp_data_key]['type'])
                            self.vo_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_A.append(client_alias)
                                    break

                            if resource_found is False:
                                self.vo_resource_host_A.append('NA')
                                self.vo_resource_hw_ver_A.append('NA')
                                self.vo_resource_eid_A.append('NA')
                                self.vo_resource_kernel_A.append('NA')
                                self.vo_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vo_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_A.append(endp_data[endp_data_key]['tos'])
                                    self.vo_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vo_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_A.append('NA')
                                self.vo_port_ssid_A.append('NA')
                                self.vo_port_mode_A.append('NA')
                                self.vo_port_traffic_type_A.append("NA")
                                self.vo_port_offered_rx_rate_A.append("NA")
                                self.vo_port_offered_tx_rate_A.append("NA")
                                self.vo_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_port_protocol_B.append(endp_data[endp_data_key]['type'])
                            self.vo_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource may need to have try except to handle cases where
                            # there is an issue getting data
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vo_resource_host_B.append('NA')
                                self.vo_resource_hw_ver_B.append('NA')
                                self.vo_resource_eid_B.append('NA')
                                self.vo_resource_kernel_B.append('NA')
                                self.vo_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vo_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_B.append(endp_data[endp_data_key]['tos'])
                                    self.vo_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vo_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_B.append('NA')
                                self.vo_port_ssid_B.append('NA')
                                self.vo_port_mode_B.append('NA')
                                self.vo_port_traffic_type_B.append("NA")
                                self.vo_port_offered_rx_rate_B.append("NA")
                                self.vo_port_offered_tx_rate_B.append("NA")
                                self.vo_port_channel_B.append("NA")

            # type field and tos not supported in 5.4.6 so this is for backward compatibility
            # Use the END name  for type and TOS
            else:
                if 'MLT' in endp_data[endp_data_key]['name']:    # type
                    if 'BK' in endp_data[endp_data_key]['name']:  # tos
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.bk_port_protocol_A.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.bk_resource_host_A.append('NA')
                                self.bk_resource_hw_ver_A.append('NA')
                                self.bk_resource_eid_A.append('NA')
                                self.bk_resource_kernel_A.append('NA')
                                self.bk_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.bk_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_A.append('BK')
                                    self.bk_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.bk_port_offered_tx_rate_A.append('0')
                                    self.bk_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_A.append('NA')
                                self.bk_port_ssid_A.append('NA')
                                self.bk_port_mode_A.append('NA')
                                self.bk_port_traffic_type_A.append("NA")
                                self.bk_port_offered_rx_rate_A.append("NA")
                                self.bk_port_offered_tx_rate_A.append("NA")
                                self.bk_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.bk_port_protocol_B.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_B.append(client_alias)
                                    break

                            if resource_found is False:
                                self.bk_resource_host_B.append('NA')
                                self.bk_resource_hw_ver_B.append('NA')
                                self.bk_resource_eid_B.append('NA')
                                self.bk_resource_kernel_B.append('NA')
                                self.bk_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.bk_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_B.append('BK')
                                    self.bk_port_offered_rx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.bk_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_B.append('NA')
                                self.bk_port_ssid_B.append('NA')
                                self.bk_port_mode_B.append('NA')
                                self.bk_port_traffic_type_B.append("NA")
                                self.bk_port_offered_rx_rate_B.append("NA")
                                self.bk_port_offered_tx_rate_B.append("NA")
                                self.bk_port_channel_B.append("NA")

                    elif 'BE' in endp_data[endp_data_key]['name']:  # tos
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.be_clients_A.append(endp_data[endp_data_key]['name'])
                            self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.be_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.be_port_protocol_A.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_A.append(client_alias)
                                    break

                            if resource_found is False:
                                self.be_resource_host_A.append('NA')
                                self.be_resource_hw_ver_A.append('NA')
                                self.be_resource_eid_A.append('NA')
                                self.be_resource_kernel_A.append('NA')
                                self.be_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.be_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_A.append('BE')
                                    self.be_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.be_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_A.append('NA')
                                self.be_port_ssid_A.append('NA')
                                self.be_port_mode_A.append('NA')
                                self.be_port_traffic_type_A.append("NA")
                                self.be_port_offered_rx_rate_A.append("NA")
                                self.be_port_offered_tx_rate_A.append("NA")
                                self.be_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.be_clients_B.append(endp_data[endp_data_key]['name'])
                            self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.be_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.be_port_protocol_B.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.be_resource_host_B.append('NA')
                                self.be_resource_hw_ver_B.append('NA')
                                self.be_resource_eid_B.append('NA')
                                self.be_resource_kernel_B.append('NA')
                                self.be_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.be_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_B.append('BE')
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.be_port_offered_rx_rate_B.append('0')
                                    self.be_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_B.append('NA')
                                self.be_port_ssid_B.append('NA')
                                self.be_port_mode_B.append('NA')
                                self.be_port_traffic_type_B.append("NA")
                                self.be_port_offered_rx_rate_B.append("NA")
                                self.be_port_offered_tx_rate_B.append("NA")
                                self.be_port_channel_B.append("NA")

                    elif 'VI' in endp_data[endp_data_key]['name']:  # tos
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.vi_port_protocol_A.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_A.append('NA')
                                self.vi_resource_hw_ver_A.append('NA')
                                self.vi_resource_eid_A.append('NA')
                                self.vi_resource_kernel_A.append('NA')
                                self.vi_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vi_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_A.append('VI')
                                    self.vi_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.vi_port_offered_tx_rate_A.append('0')
                                    self.vi_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_A.append('NA')
                                self.vi_port_ssid_A.append('NA')
                                self.vi_port_mode_A.append('NA')
                                self.vi_port_traffic_type_A.append("NA")
                                self.vi_port_offered_rx_rate_A.append("NA")
                                self.vi_port_offered_tx_rate_A.append("NA")
                                self.vi_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.vi_port_protocol_B.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_B.append('NA')
                                self.vi_resource_hw_ver_B.append('NA')
                                self.vi_resource_eid_B.append('NA')
                                self.vi_resource_kernel_B.append('NA')
                                self.vi_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vi_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_B.append('VI')
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.vi_port_offered_rx_rate_B.append('0')
                                    self.vi_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vi_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_B.append('NA')
                                self.vi_port_ssid_B.append('NA')
                                self.vi_port_mode_B.append('NA')
                                self.vi_port_traffic_type_B.append("NA")
                                self.vi_port_offered_rx_rate_B.append("NA")
                                self.vi_port_offered_tx_rate_B.append("NA")
                                self.vi_port_channel_B.append("NA")

                    elif 'VO' in endp_data[endp_data_key]['name']:
                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.vo_port_protocol_A.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_A.append(client_alias)
                                    break

                            if resource_found is False:
                                self.vo_resource_host_A.append('NA')
                                self.vo_resource_hw_ver_A.append('NA')
                                self.vo_resource_eid_A.append('NA')
                                self.vo_resource_kernel_A.append('NA')
                                self.vo_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vo_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_A.append('VO')
                                    self.vo_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vo_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_A.append('NA')
                                self.vo_port_ssid_A.append('NA')
                                self.vo_port_mode_A.append('NA')
                                self.vo_port_traffic_type_A.append("NA")
                                self.vo_port_offered_rx_rate_A.append("NA")
                                self.vo_port_offered_tx_rate_A.append("NA")
                                self.vo_port_channel_A.append("NA")

                        # for multicast the logic is reversed. A is upstream for multicast, B is
                        # downstream for multicast
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.vo_port_protocol_B.append('Mcast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vo_resource_host_B.append('NA')
                                self.vo_resource_hw_ver_B.append('NA')
                                self.vo_resource_eid_B.append('NA')
                                self.vo_resource_kernel_B.append('NA')
                                self.vo_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[3]

                            port_found = False
                            self.vo_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_B.append('VO')
                                    # (self.cx_profile.side_a_min_bps) # a side tx
                                    self.vo_port_offered_rx_rate_B.append('0')
                                    self.vo_port_offered_tx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_B.append('NA')
                                self.vo_port_ssid_B.append('NA')
                                self.vo_port_mode_B.append('NA')
                                self.vo_port_traffic_type_B.append("NA")
                                self.vo_port_offered_rx_rate_B.append("NA")
                                self.vo_port_offered_tx_rate_B.append("NA")
                                self.vo_port_channel_B.append("NA")

                # for unicast the upstream is B and downstream is A
                # note for B tx is download and rx is uploat
                else:
                    if 'BK' in endp_data[endp_data_key]['name']:
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.bk_port_protocol_A.append('Uni-Cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.bk_resource_host_A.append('NA')
                                self.bk_resource_hw_ver_A.append('NA')
                                self.bk_resource_eid_A.append('NA')
                                self.bk_resource_kernel_A.append('NA')
                                self.bk_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.bk_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_A.append('BK')
                                    self.bk_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.bk_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_A.append('NA')
                                self.bk_port_ssid_A.append('NA')
                                self.bk_port_mode_A.append('NA')
                                self.bk_port_traffic_type_A.append("NA")
                                self.bk_port_offered_rx_rate_A.append("NA")
                                self.bk_port_offered_tx_rate_A.append("NA")
                                self.bk_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.bk_port_protocol_B.append('Uni-cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.bk_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.bk_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.bk_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.bk_resource_alias_B.append(client_alias)
                                    break

                            if resource_found is False:
                                self.bk_resource_host_B.append('NA')
                                self.bk_resource_hw_ver_B.append('NA')
                                self.bk_resource_eid_B.append('NA')
                                self.bk_resource_kernel_B.append('NA')
                                self.bk_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.bk_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.bk_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.bk_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_B.append('BK')
                                    self.bk_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.bk_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.bk_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.bk_port_mac_B.append('NA')
                                self.bk_port_ssid_B.append('NA')
                                self.bk_port_mode_B.append('NA')
                                self.bk_port_traffic_type_B.append("NA")
                                self.bk_port_offered_rx_rate_B.append("NA")
                                self.bk_port_offered_tx_rate_B.append("NA")
                                self.bk_port_channel_B.append("NA")

                    # for unicast the upstream is B and downstream is A
                    elif 'BE' in endp_data[endp_data_key]['name']:

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.be_clients_A.append(endp_data[endp_data_key]['name'])
                            self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.be_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.be_port_protocol_A.append('Uni-cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_A.append(client_alias)
                                    break

                            if resource_found is False:
                                self.be_resource_host_A.append('NA')
                                self.be_resource_hw_ver_A.append('NA')
                                self.be_resource_eid_A.append('NA')
                                self.be_resource_kernel_A.append('NA')
                                self.be_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.be_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_A.append('BE')
                                    self.be_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.be_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_A.append('NA')
                                self.be_port_ssid_A.append('NA')
                                self.be_port_mode_A.append('NA')
                                self.be_port_traffic_type_A.append("NA")
                                self.be_port_offered_rx_rate_A.append("NA")
                                self.be_port_offered_tx_rate_A.append("NA")
                                self.be_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.be_clients_B.append(endp_data[endp_data_key]['name'])
                            self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.be_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.be_port_protocol_B.append('Uni-cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.be_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.be_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.be_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.be_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.be_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.be_resource_host_B.append('NA')
                                self.be_resource_hw_ver_B.append('NA')
                                self.be_resource_eid_B.append('NA')
                                self.be_resource_kernel_B.append('NA')
                                self.be_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.be_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.be_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.be_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.be_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.be_port_traffic_type_B.append('BE')
                                    self.be_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.be_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.be_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.be_port_mac_B.append('NA')
                                self.be_port_ssid_B.append('NA')
                                self.be_port_mode_B.append('NA')
                                self.be_port_traffic_type_B.append("NA")
                                self.be_port_offered_rx_rate_B.append("NA")
                                self.be_port_offered_tx_rate_B.append("NA")
                                self.be_port_channel_B.append("NA")

                    elif 'VI' in endp_data[endp_data_key]['name']:
                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.vi_port_protocol_A.append('Uni-cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_A.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_A.append('NA')
                                self.vi_resource_hw_ver_A.append('NA')
                                self.vi_resource_eid_A.append('NA')
                                self.vi_resource_kernel_A.append('NA')
                                self.vi_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vi_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_A.append('VI')
                                    self.vi_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vi_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vi_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_A.append('NA')
                                self.vi_port_ssid_A.append('NA')
                                self.vi_port_mode_A.append('NA')
                                self.vi_port_traffic_type_A.append("NA")
                                self.vi_port_offered_rx_rate_A.append("NA")
                                self.vi_port_offered_tx_rate_A.append("NA")
                                self.vi_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vi_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.vi_port_protocol_B.append('Uni-cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vi_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vi_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vi_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vi_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vi_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vi_resource_host_B.append('NA')
                                self.vi_resource_hw_ver_B.append('NA')
                                self.vi_resource_eid_B.append('NA')
                                self.vi_resource_kernel_B.append('NA')
                                self.vi_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vi_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vi_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vi_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vi_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vi_port_traffic_type_B.append('VI')
                                    self.vi_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vi_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vi_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vi_port_mac_B.append('NA')
                                self.vi_port_ssid_B.append('NA')
                                self.vi_port_mode_B.append('NA')
                                self.vi_port_traffic_type_B.append("NA")
                                self.vi_port_offered_rx_rate_B.append("NA")
                                self.vi_port_offered_tx_rate_B.append("NA")
                                self.vi_port_channel_B.append("NA")

                    elif 'VO' in endp_data[endp_data_key]['name']:
                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_rx_drop_percent_A.append(endp_data[endp_data_key]["rx drop %"])
                            self.vo_port_protocol_A.append('Uni-cast')

                            # Report Table information
                            # use the eid to get the hostname and channel
                            eid_tmp_resource = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[
                                                   0]) + '.' + str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_A.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_A.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_A.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_A.append(client_alias)
                                    break

                            if resource_found is False:
                                self.vo_resource_host_A.append('NA')
                                self.vo_resource_hw_ver_A.append('NA')
                                self.vo_resource_eid_A.append('NA')
                                self.vo_resource_kernel_A.append('NA')
                                self.vo_resource_alias_A.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vo_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_A.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_A.append('VO')
                                    self.vo_port_offered_rx_rate_A.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_offered_tx_rate_A.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vo_port_channel_A.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_A.append('NA')
                                self.vo_port_ssid_A.append('NA')
                                self.vo_port_mode_A.append('NA')
                                self.vo_port_traffic_type_A.append("NA")
                                self.vo_port_offered_rx_rate_A.append("NA")
                                self.vo_port_offered_tx_rate_A.append("NA")
                                self.vo_port_channel_A.append("NA")

                        # for unicast the upstream is B and downstream is A
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.vo_rx_drop_percent_B.append(endp_data[endp_data_key]["rx drop %"])
                            self.vo_port_protocol_B.append('Uni-cast')

                            # look up the resource
                            resource_found = False
                            for resource_data in self.resource_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resource:
                                    resource_found = True
                                    self.vo_resource_host_B.append(resource_data[resource_data_key]['hostname'])
                                    self.vo_resource_hw_ver_B.append(resource_data[resource_data_key]['hw version'])
                                    self.vo_resource_eid_B.append(resource_data[resource_data_key]['eid'])
                                    self.vo_resource_kernel_B.append(resource_data[resource_data_key]['kernel'])
                                    client_alias = self.create_resource_alias(
                                        eid=resource_data[resource_data_key]['eid'],
                                        host=resource_data[resource_data_key]['hostname'],
                                        hw_version=resource_data[resource_data_key]['hw version'],
                                        kernel=resource_data[resource_data_key]['kernel'])
                                    self.vo_resource_alias_B.append(client_alias)

                                    break

                            if resource_found is False:
                                self.vo_resource_host_B.append('NA')
                                self.vo_resource_hw_ver_B.append('NA')
                                self.vo_resource_eid_B.append('NA')
                                self.vo_resource_kernel_B.append('NA')
                                self.vo_resource_alias_B.append('NA')

                            # look up port information
                            eid_info = endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resource + '.' + eid_info[1]

                            port_found = False
                            self.vo_port_eid_B.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.vo_port_mac_B.append(port_data[port_data_key]['mac'])
                                    self.vo_port_ssid_B.append(port_data[port_data_key]['ssid'])
                                    self.vo_port_mode_B.append(port_data[port_data_key]['mode'])
                                    self.vo_port_traffic_type_B.append('VO')
                                    self.vo_port_offered_rx_rate_B.append(self.cx_profile.side_b_min_bps)  # b side tx
                                    self.vo_port_offered_tx_rate_B.append(self.cx_profile.side_a_min_bps)  # a side tx
                                    self.vo_port_channel_B.append(port_data[port_data_key]["channel"])
                                    port_found = True
                                    break

                            if port_found is False:
                                self.vo_port_mac_B.append('NA')
                                self.vo_port_ssid_B.append('NA')
                                self.vo_port_mode_B.append('NA')
                                self.vo_port_traffic_type_B.append("NA")
                                self.vo_port_offered_rx_rate_B.append("NA")
                                self.vo_port_offered_tx_rate_B.append("NA")
                                self.vo_port_channel_B.append("NA")

        self.client_dict_A = {
            "y_axis_name": "Client names",
            "x_axis_name": "Throughput in Mbps",
            "min_bps_a": self.side_a_min_bps,
            "min_bps_b": self.side_b_min_bps,
            "BK": {
                "colors": ['orange', 'wheat'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.bk_clients_A,
                "ul_A": self.bk_tos_ul_A,
                "dl_A": self.bk_tos_dl_A,
                "resource_alias_A": self.bk_resource_alias_A,
                "resource_host_A": self.bk_resource_host_A,
                "resource_hw_ver_A": self.bk_resource_hw_ver_A,
                "resource_eid_A": self.bk_resource_eid_A,
                "resource_kernel_A": self.bk_resource_kernel_A,
                "port_A": self.bk_port_eid_A,
                "mac_A": self.bk_port_mac_A,
                "ssid_A": self.bk_port_ssid_A,
                "channel_A": self.bk_port_channel_A,
                "mode_A": self.bk_port_mode_A,
                "traffic_type_A": self.bk_port_traffic_type_A,
                "traffic_protocol_A": self.bk_port_protocol_A,
                "offered_download_rate_A": self.bk_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.bk_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.bk_rx_drop_percent_A,

                # B side
                "clients_B": self.bk_clients_B,
                "ul_B": self.bk_tos_ul_B,
                "dl_B": self.bk_tos_dl_B,
                "resource_alias_B": self.bk_resource_alias_B,
                "resource_host_B": self.bk_resource_host_B,
                "resource_hw_ver_B": self.bk_resource_hw_ver_B,
                "resource_eid_B": self.bk_resource_eid_B,
                "resource_kernel_B": self.bk_resource_kernel_B,
                "port_B": self.bk_port_eid_B,
                "mac_B": self.bk_port_mac_B,
                "ssid_B": self.bk_port_ssid_B,
                "channel_B": self.bk_port_channel_B,
                "mode_B": self.bk_port_mode_B,
                "traffic_type_B": self.bk_port_traffic_type_B,
                "traffic_protocol_B": self.bk_port_protocol_B,
                "offered_download_rate_B": self.bk_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.bk_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.bk_rx_drop_percent_B,

            },
            "BE": {
                "colors": ['lightcoral', 'mistyrose'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.be_clients_A,
                "ul_A": self.be_tos_ul_A,
                "dl_A": self.be_tos_dl_A,
                "resource_alias_A": self.be_resource_alias_A,
                "resource_host_A": self.be_resource_host_A,
                "resource_hw_ver_A": self.be_resource_hw_ver_A,
                "resource_eid_A": self.be_resource_eid_A,
                "resource_kernel_A": self.be_resource_kernel_A,
                "port_A": self.be_port_eid_A,
                "mac_A": self.be_port_mac_A,
                "ssid_A": self.be_port_ssid_A,
                "channel_A": self.be_port_channel_A,
                "mode_A": self.be_port_mode_A,
                "traffic_type_A": self.be_port_traffic_type_A,
                "traffic_protocol_A": self.be_port_protocol_A,
                "offered_download_rate_A": self.be_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.be_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.be_rx_drop_percent_A,

                # B side
                "clients_B": self.be_clients_B,
                "ul_B": self.be_tos_ul_B,
                "dl_B": self.be_tos_dl_B,
                "resource_alias_B": self.be_resource_alias_B,
                "resource_host_B": self.be_resource_host_B,
                "resource_hw_ver_B": self.be_resource_hw_ver_B,
                "resource_eid_B": self.be_resource_eid_B,
                "resource_kernel_B": self.be_resource_kernel_B,
                "port_B": self.be_port_eid_B,
                "mac_B": self.be_port_mac_B,
                "ssid_B": self.be_port_ssid_B,
                "channel_B": self.be_port_channel_B,
                "mode_B": self.be_port_mode_B,
                "traffic_type_B": self.be_port_traffic_type_B,
                "traffic_protocol_B": self.be_port_protocol_B,
                "offered_download_rate_B": self.be_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.be_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.be_rx_drop_percent_B,

            },
            "VI": {
                "colors": ['steelblue', 'lightskyblue'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.vi_clients_A,
                "ul_A": self.vi_tos_ul_A,
                "dl_A": self.vi_tos_dl_A,
                "resource_alias_A": self.vi_resource_alias_A,
                "resource_host_A": self.vi_resource_host_A,
                "resource_hw_ver_A": self.vi_resource_hw_ver_A,
                "resource_eid_A": self.vi_resource_eid_A,
                "resource_kernel_A": self.vi_resource_kernel_A,
                "port_A": self.vi_port_eid_A,
                "mac_A": self.vi_port_mac_A,
                "ssid_A": self.vi_port_ssid_A,
                "channel_A": self.vi_port_channel_A,
                "mode_A": self.vi_port_mode_A,
                "traffic_type_A": self.vi_port_traffic_type_A,
                "traffic_protocol_A": self.vi_port_protocol_A,
                "offered_download_rate_A": self.vi_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.vi_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.vi_rx_drop_percent_A,

                # B side
                "clients_B": self.vi_clients_B,
                "ul_B": self.vi_tos_ul_B,
                "dl_B": self.vi_tos_dl_B,
                "resource_alias_B": self.vi_resource_alias_B,
                "resource_host_B": self.vi_resource_host_B,
                "resource_hw_ver_B": self.vi_resource_hw_ver_B,
                "resource_eid_B": self.vi_resource_eid_B,
                "resource_kernel_B": self.vi_resource_kernel_B,
                "port_B": self.vi_port_eid_B,
                "mac_B": self.vi_port_mac_B,
                "ssid_B": self.vi_port_ssid_B,
                "channel_B": self.vi_port_channel_B,
                "mode_B": self.vi_port_mode_B,
                "traffic_type_B": self.vi_port_traffic_type_B,
                "traffic_protocol_B": self.vi_port_protocol_B,
                "offered_download_rate_B": self.vi_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.vi_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.vi_rx_drop_percent_B,

            },
            "VO": {
                "colors": ['green', 'lightgreen'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.vo_clients_A,
                "ul_A": self.vo_tos_ul_A,
                "dl_A": self.vo_tos_dl_A,
                "resource_alias_A": self.vo_resource_alias_A,
                "resource_host_A": self.vo_resource_host_A,
                "resource_hw_ver_A": self.vo_resource_hw_ver_A,
                "resource_eid_A": self.vo_resource_eid_A,
                "resource_kernel_A": self.vo_resource_kernel_A,
                "port_A": self.vo_port_eid_A,
                "mac_A": self.vo_port_mac_A,
                "ssid_A": self.vo_port_ssid_A,
                "channel_A": self.vo_port_channel_A,
                "mode_A": self.vo_port_mode_A,
                "traffic_type_A": self.vo_port_traffic_type_A,
                "traffic_protocol_A": self.vo_port_protocol_A,
                "offered_download_rate_A": self.vo_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.vo_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.vo_rx_drop_percent_A,

                # B side
                "clients_B": self.vo_clients_B,
                "ul_B": self.vo_tos_ul_B,
                "dl_B": self.vo_tos_dl_B,
                "resource_alias_B": self.vo_resource_host_B,
                "resource_host_B": self.vo_resource_host_B,
                "resource_hw_ver_B": self.vo_resource_hw_ver_B,
                "resource_eid_B": self.vo_resource_eid_B,
                "resource_kernel_B": self.vo_resource_kernel_B,
                "port_B": self.vo_port_eid_B,
                "mac_B": self.vo_port_mac_B,
                "ssid_B": self.vo_port_ssid_B,
                "channel_B": self.vo_port_channel_B,
                "mode_B": self.vo_port_mode_B,
                "traffic_type_B": self.vo_port_traffic_type_B,
                "traffic_protocol_B": self.vo_port_protocol_B,
                "offered_download_rate_B": self.vo_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.vo_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.vo_rx_drop_percent_B,

            }
        }

        self.client_dict_B = {
            "y_axis_name": "Client names",
            "x_axis_name": "Throughput in Mbps",
            "min_bps_a": self.side_a_min_bps,
            "min_bps_b": self.side_b_min_bps,
            "BK": {
                "colors": ['orange', 'wheat'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.bk_clients_A,
                "ul_A": self.bk_tos_ul_A,
                "dl_A": self.bk_tos_dl_A,
                "resource_alias_A": self.bk_resource_alias_A,
                "resource_host_A": self.bk_resource_host_A,
                "resource_hw_ver_A": self.bk_resource_hw_ver_A,
                "resource_eid_A": self.bk_resource_eid_A,
                "resource_kernel_A": self.bk_resource_kernel_A,
                "port_A": self.bk_port_eid_A,
                "mac_A": self.bk_port_mac_A,
                "ssid_A": self.bk_port_ssid_A,
                "channel_A": self.bk_port_channel_A,
                "mode_A": self.bk_port_mode_A,
                "traffic_type_A": self.bk_port_traffic_type_A,
                "traffic_protocol_A": self.bk_port_protocol_A,
                "offered_download_rate_A": self.bk_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.bk_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.bk_rx_drop_percent_A,

                # B side
                "clients_B": self.bk_clients_B,
                "ul_B": self.bk_tos_ul_B,
                "dl_B": self.bk_tos_dl_B,
                "resource_alias_B": self.bk_resource_alias_B,
                "resource_host_B": self.bk_resource_host_B,
                "resource_hw_ver_B": self.bk_resource_hw_ver_B,
                "resource_eid_B": self.bk_resource_eid_B,
                "resource_kernel_B": self.bk_resource_kernel_B,
                "port_B": self.bk_port_eid_B,
                "mac_B": self.bk_port_mac_B,
                "ssid_B": self.bk_port_ssid_B,
                "channel_B": self.bk_port_channel_B,
                "mode_B": self.bk_port_mode_B,
                "traffic_type_B": self.bk_port_traffic_type_B,
                "traffic_protocol_B": self.bk_port_protocol_B,
                "offered_download_rate_B": self.bk_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.bk_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.bk_rx_drop_percent_B,

            },
            "BE": {
                "colors": ['lightcoral', 'mistyrose'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.be_clients_A,
                "ul_A": self.be_tos_ul_A,
                "dl_A": self.be_tos_dl_A,
                "resource_alias_A": self.be_resource_alias_A,
                "resource_host_A": self.be_resource_host_A,
                "resource_hw_ver_A": self.be_resource_hw_ver_A,
                "resource_eid_A": self.be_resource_eid_A,
                "resource_kernel_A": self.be_resource_kernel_A,
                "port_A": self.be_port_eid_A,
                "mac_A": self.be_port_mac_A,
                "ssid_A": self.be_port_ssid_A,
                "channel_A": self.be_port_channel_A,
                "mode_A": self.be_port_mode_A,
                "traffic_type_A": self.be_port_traffic_type_A,
                "traffic_protocol_A": self.be_port_protocol_A,
                "offered_download_rate_A": self.be_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.be_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.be_rx_drop_percent_A,

                # B side
                "clients_B": self.be_clients_B,
                "ul_B": self.be_tos_ul_B,
                "dl_B": self.be_tos_dl_B,
                "resource_alias_B": self.be_resource_alias_B,
                "resource_host_B": self.be_resource_host_B,
                "resource_hw_ver_B": self.be_resource_hw_ver_B,
                "resource_eid_B": self.be_resource_eid_B,
                "resource_kernel_B": self.be_resource_kernel_B,
                "port_B": self.be_port_eid_B,
                "mac_B": self.be_port_mac_B,
                "ssid_B": self.be_port_ssid_B,
                "channel_B": self.be_port_channel_B,
                "mode_B": self.be_port_mode_B,
                "traffic_type_B": self.be_port_traffic_type_B,
                "traffic_protocol_B": self.be_port_protocol_B,
                "offered_download_rate_B": self.be_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.be_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.be_rx_drop_percent_B,

            },
            "VI": {
                "colors": ['steelblue', 'lightskyblue'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.vi_clients_A,
                "ul_A": self.vi_tos_ul_A,
                "dl_A": self.vi_tos_dl_A,
                "resource_alias_A": self.vi_resource_alias_A,
                "resource_host_A": self.vi_resource_host_A,
                "resource_hw_ver_A": self.vi_resource_hw_ver_A,
                "resource_eid_A": self.vi_resource_eid_A,
                "resource_kernel_A": self.vi_resource_kernel_A,
                "port_A": self.vi_port_eid_A,
                "mac_A": self.vi_port_mac_A,
                "ssid_A": self.vi_port_ssid_A,
                "channel_A": self.vi_port_channel_A,
                "mode_A": self.vi_port_mode_A,
                "traffic_type_A": self.vi_port_traffic_type_A,
                "traffic_protocol_A": self.vi_port_protocol_A,
                "offered_download_rate_A": self.vi_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.vi_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.vi_rx_drop_percent_A,

                # B side
                "clients_B": self.vi_clients_B,
                "ul_B": self.vi_tos_ul_B,
                "dl_B": self.vi_tos_dl_B,
                "resource_alias_B": self.vi_resource_alias_B,
                "resource_host_B": self.vi_resource_host_B,
                "resource_hw_ver_B": self.vi_resource_hw_ver_B,
                "resource_eid_B": self.vi_resource_eid_B,
                "resource_kernel_B": self.vi_resource_kernel_B,
                "port_B": self.vi_port_eid_B,
                "mac_B": self.vi_port_mac_B,
                "ssid_B": self.vi_port_ssid_B,
                "channel_B": self.vi_port_channel_B,
                "mode_B": self.vi_port_mode_B,
                "traffic_type_B": self.vi_port_traffic_type_B,
                "traffic_protocol_B": self.vi_port_protocol_B,
                "offered_download_rate_B": self.vi_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.vi_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.vi_rx_drop_percent_B,

            },
            "VO": {
                "colors": ['green', 'lightgreen'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.vo_clients_A,
                "ul_A": self.vo_tos_ul_A,
                "dl_A": self.vo_tos_dl_A,
                "resource_alias_A": self.vo_resource_alias_A,
                "resource_host_A": self.vo_resource_host_A,
                "resource_hw_ver_A": self.vo_resource_hw_ver_A,
                "resource_eid_A": self.vo_resource_eid_A,
                "resource_kernel_A": self.vo_resource_kernel_A,
                "port_A": self.vo_port_eid_A,
                "mac_A": self.vo_port_mac_A,
                "ssid_A": self.vo_port_ssid_A,
                "channel_A": self.vo_port_channel_A,
                "mode_A": self.vo_port_mode_A,
                "traffic_type_A": self.vo_port_traffic_type_A,
                "traffic_protocol_A": self.vo_port_protocol_A,
                "offered_download_rate_A": self.vo_port_offered_rx_rate_A,
                "offered_upload_rate_A": self.vo_port_offered_tx_rate_A,
                "download_rx_drop_percent_A": self.vo_rx_drop_percent_A,

                # B side
                "clients_B": self.vo_clients_B,
                "ul_B": self.vo_tos_ul_B,
                "dl_B": self.vo_tos_dl_B,
                "resource_alias_B": self.vo_resource_alias_B,
                "resource_host_B": self.vo_resource_host_B,
                "resource_hw_ver_B": self.vo_resource_hw_ver_B,
                "resource_eid_B": self.vo_resource_eid_B,
                "resource_kernel_B": self.vo_resource_kernel_B,
                "port_B": self.vo_port_eid_B,
                "mac_B": self.vo_port_mac_B,
                "ssid_B": self.vo_port_ssid_B,
                "channel_B": self.vo_port_channel_B,
                "mode_B": self.vo_port_mode_B,
                "traffic_type_B": self.vo_port_traffic_type_B,
                "traffic_protocol_B": self.vo_port_protocol_B,
                "offered_download_rate_B": self.vo_port_offered_tx_rate_B,
                "offered_upload_rate_B": self.vo_port_offered_rx_rate_B,
                "download_rx_drop_percent_B": self.vo_rx_drop_percent_B,

            }
        }

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
            'Ul-Rx-Drop_Percent',
            'Dl-Rx-Goodput-bps',
            'Dl-Rx-Rate-ll',
            'Dl-Rx-Pkts-ll',
            'DL-Rx-Drop-Percent']

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
            'Ul-Rx-Drop_Percent',
            'Dl-Rx-Goodput-bps',
            'Dl-Rx-Rate-ll',
            'Dl-Rx-Pkts-ll',
            'Dl-Rx-Drop-Percent']
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

    def set_report_obj(self, report):
        self.report = report

    def set_dut_info(self,
                     dut_model_num: str = 'Not Set',
                     dut_hw_version: str = 'Not Set',
                     dut_sw_version: str = 'Not Set',
                     dut_serial_num: str = 'Not Set'):
        self.dut_model_num = dut_model_num
        self.dut_hw_version = dut_hw_version
        self.dut_sw_version = dut_sw_version
        self.dut_serial_num = dut_serial_num

    def generate_report(self,):
        self.report.set_obj_html("Objective", "The Layer 3 Traffic Generation Test is designed to test the performance of the "
                                 "Access Point by running layer 3 Cross-Connect Traffic.  Layer-3 Cross-Connects represent a stream "
                                 "of data flowing through the system under test. A Cross-Connect (CX) is composed of two Endpoints, "
                                 "each of which is associated with a particular Port (physical or virtual interface).")

        self.report.build_objective()

        test_setup_info = {
            "DUT Name": self.dut_model_num,
            "DUT Hardware Version": self.dut_hw_version,
            "DUT Software Version": self.dut_sw_version,
            "DUT Serial Number": self.dut_serial_num,
        }

        self.report.set_table_title("Device Under Test Information")
        self.report.build_table_title()
        self.report.test_setup_table(value="Device Under Test",
                                     test_setup_data=test_setup_info)

        test_input_info = {
            "LANforge ip": self.lfmgr,
            "LANforge port": self.lfmgr_port,
            "Upstream": self.upstream_port,
            "Test Duration": self.test_duration,
            "Polling Interval": self.polling_interval,
            "Total No. of Devices": self.station_count,
        }

        self.report.set_table_title("Test Configuration")
        self.report.build_table_title()
        self.report.test_setup_table(value="Test Configuration",
                                     test_setup_data=test_input_info)

        self.report.set_table_title("Radio Configuration")
        self.report.build_table_title()

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
                self.radio_name_list,
                self.ssid_list,
                self.ssid_password_list,
                self.ssid_security_list,
                self.wifi_mode_list,
                self.enable_flags_list,
                self.reset_port_enable_list,
                self.reset_port_time_min_list,
                self.reset_port_time_max_list):

            mode_value = wifi_mode_dict[int(mode_)]

            radio_info = {
                "SSID": ssid_,
                "Security": ssid_security_,
                "Wifi mode set": mode_value,
                'Wifi Enable Flags': wifi_enable_flags_list_
            }
            self.report.test_setup_table(value=radio_, test_setup_data=radio_info)

        # TODO move the graphing to the class so it may be called as a service

        # Graph TOS data
        # Once the data is stopped can collect the data for the cx's both multi cast and uni cast
        # if the traffic is still running will gather the running traffic
        self.evaluate_qos()

        # graph BK A
        # try to do as a loop
        tos_list = ['BK', 'BE', 'VI', 'VO']

        for tos in tos_list:
            if (self.client_dict_A[tos]["ul_A"] and self.client_dict_A[tos]["dl_A"]):
                min_bps_a = self.client_dict_A["min_bps_a"]
                min_bps_b = self.client_dict_A["min_bps_b"]

                dataset_list = [self.client_dict_A[tos]["ul_A"], self.client_dict_A[tos]["dl_A"]]
                # TODO possibly explain the wording for upload and download
                dataset_length = len(self.client_dict_A[tos]["ul_A"])
                x_fig_size = 20
                y_fig_size = len(self.client_dict_A[tos]["clients_A"]) * .4 + 5
                logger.debug("length of clients_A {clients} resource_alias_A {alias_A}".format(
                    clients=len(self.client_dict_A[tos]["clients_A"]), alias_A=len(self.client_dict_A[tos]["resource_alias_A"])))
                logger.debug("clients_A {clients}".format(clients=self.client_dict_A[tos]["clients_A"]))
                logger.debug("resource_alias_A {alias_A}".format(alias_A=self.client_dict_A[tos]["resource_alias_A"]))

                if int(min_bps_a) != 0:
                    self.report.set_obj_html(
                        _obj_title=f"Individual throughput measured  upload tcp or udp bps: {min_bps_a},  download tcp, udp, or mcast  bps: {min_bps_b} station for traffic {tos} (WiFi).",
                        _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                        f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                        f"Throughput in Mbps”.")
                else:
                    self.report.set_obj_html(
                        _obj_title=f"Individual throughput mcast download bps: {min_bps_b} traffic {tos} (WiFi).",
                        _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                        f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                        f"Throughput in Mbps”.")

                self.report.build_objective()

                graph = lf_graph.lf_bar_graph_horizontal(_data_set=dataset_list,
                                                         _xaxis_name="Throughput in bps",
                                                         _yaxis_name="Client names",
                                                         # _yaxis_categories=self.client_dict_A[tos]["clients_A"],
                                                         _yaxis_categories=self.client_dict_A[tos]["resource_alias_A"],
                                                         _graph_image_name=f"{tos}_A",
                                                         _label=self.client_dict_A[tos]['labels'],
                                                         _color_name=self.client_dict_A[tos]['colors'],
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
                self.report.set_graph_image(graph_png)
                self.report.move_graph_image()
                self.report.build_graph()
                self.report.set_csv_filename(graph_png)
                self.report.move_csv_file()

                tos_dataframe_A = {
                    " Client Alias ": self.client_dict_A[tos]['resource_alias_A'],
                    " Host eid ": self.client_dict_A[tos]['resource_eid_A'],
                    " Host Name ": self.client_dict_A[tos]['resource_host_A'],
                    " Device Type / Hw Ver ": self.client_dict_A[tos]['resource_hw_ver_A'],
                    " Endp Name": self.client_dict_A[tos]["clients_A"],
                    # TODO : port A being set to many times
                    " Port Name ": self.client_dict_A[tos]['port_A'],
                    " Mode ": self.client_dict_A[tos]['mode_A'],
                    " Mac ": self.client_dict_A[tos]['mac_A'],
                    " SSID ": self.client_dict_A[tos]['ssid_A'],
                    " Channel ": self.client_dict_A[tos]['channel_A'],
                    " Type of traffic ": self.client_dict_A[tos]['traffic_type_A'],
                    " Traffic Protocol ": self.client_dict_A[tos]['traffic_protocol_A'],
                    " Offered Upload Rate Per Client": self.client_dict_A[tos]['offered_upload_rate_A'],
                    " Offered Download Rate Per Client": self.client_dict_A[tos]['offered_download_rate_A'],
                    " Upload Rate Per Client": self.client_dict_A[tos]['ul_A'],
                    " Download Rate Per Client": self.client_dict_A[tos]['dl_A'],
                    " Drop Percentage (%)": self.client_dict_A[tos]['download_rx_drop_percent_A']
                }

                dataframe3 = pd.DataFrame(tos_dataframe_A)
                self.report.set_table_dataframe(dataframe3)
                self.report.build_table()

        # TODO both client_dict_A and client_dict_B contains the same information
        for tos in tos_list:
            if (self.client_dict_B[tos]["ul_B"] and self.client_dict_B[tos]["dl_B"]):
                min_bps_a = self.client_dict_B["min_bps_a"]
                min_bps_b = self.client_dict_B["min_bps_b"]

                dataset_list = [self.client_dict_B[tos]["ul_B"], self.client_dict_B[tos]["dl_B"]]
                dataset_length = len(self.client_dict_B[tos]["ul_B"])

                x_fig_size = 20
                y_fig_size = len(self.client_dict_B[tos]["clients_B"]) * .4 + 5

                self.report.set_obj_html(
                    _obj_title=f"Individual throughput upstream endp,  offered upload bps: {min_bps_a} offered download bps: {min_bps_b} /station for traffic {tos} (WiFi).",
                    _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                    f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                    f"Throughput in Mbps”.")
                self.report.build_objective()

                graph = lf_graph.lf_bar_graph_horizontal(_data_set=dataset_list,
                                                         _xaxis_name="Throughput in bps",
                                                         _yaxis_name="Client names",
                                                         # _yaxis_categories=self.client_dict_B[tos]["clients_B"],
                                                         _yaxis_categories=self.client_dict_B[tos]["resource_alias_B"],
                                                         _graph_image_name=f"{tos}_B",
                                                         _label=self.client_dict_B[tos]['labels'],
                                                         _color_name=self.client_dict_B[tos]['colors'],
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
                self.report.set_graph_image(graph_png)
                self.report.move_graph_image()
                self.report.build_graph()
                self.report.set_csv_filename(graph_png)
                self.report.move_csv_file()

                tos_dataframe_B = {
                    " Client Alias ": self.client_dict_B[tos]['resource_alias_B'],
                    " Host eid ": self.client_dict_B[tos]['resource_eid_B'],
                    " Host Name ": self.client_dict_B[tos]['resource_host_B'],
                    " Device Type / HW Ver ": self.client_dict_B[tos]['resource_hw_ver_B'],
                    " Endp Name": self.client_dict_B[tos]["clients_B"],
                    # TODO get correct size
                    " Port Name ": self.client_dict_B[tos]['port_B'],
                    " Mode ": self.client_dict_B[tos]['mode_B'],
                    " Mac ": self.client_dict_B[tos]['mac_B'],
                    " SSID ": self.client_dict_B[tos]['ssid_B'],
                    " Channel ": self.client_dict_B[tos]['channel_B'],
                    " Type of traffic ": self.client_dict_B[tos]['traffic_type_B'],
                    " Traffic Protocol ": self.client_dict_B[tos]['traffic_protocol_B'],
                    " Offered Upload Rate Per Client": self.client_dict_B[tos]['offered_upload_rate_B'],
                    " Offered Download Rate Per Client": self.client_dict_B[tos]['offered_download_rate_B'],
                    " Upload Rate Per Client": self.client_dict_B[tos]['ul_B'],
                    " Download Rate Per Client": self.client_dict_B[tos]['dl_B'],
                    " Drop Percentage (%)": self.client_dict_B[tos]['download_rx_drop_percent_B']
                }

                dataframe3 = pd.DataFrame(tos_dataframe_B)
                self.report.set_table_dataframe(dataframe3)
                self.report.build_table()

        # L3 total traffic # TODO csv_results_file present yet not readable
        # self.report.set_table_title("Total Layer 3 Cross-Connect Traffic across all Stations")
        # self.report.build_table_title()
        # self.report.set_table_dataframe_from_csv(self.csv_results_file)
        # self.report.build_table()

        # empty dictionarys evaluate to false , placing tables in output
        if bool(self.dl_port_csv_files):
            for key, value in self.dl_port_csv_files.items():
                if self.csv_data_to_report:
                    # read the csv file
                    self.report.set_table_title("Layer 3 Cx Traffic  {key}".format(key=key))
                    self.report.build_table_title()
                    self.report.set_table_dataframe_from_csv(value.name)
                    self.report.build_table()

                # read in column heading and last line
                df = pd.read_csv(value.name)
                last_row = df.tail(1)
                self.report.set_table_title(
                    "Layer 3 Cx Traffic Last Reporting Interval {key}".format(key=key))
                self.report.build_table_title()
                self.report.set_table_dataframe(last_row)
                self.report.build_table()

    def write_report(self):
        """Write out HTML and PDF report as configured."""
        self.report.write_report_location()
        self.report.write_html_with_timestamp()
        self.report.write_index_html()
        # report.write_pdf(_page_size = 'A3', _orientation='Landscape')
        # report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
        if platform.system() == 'Linux':
            self.report.write_pdf_with_timestamp(_page_size='A3', _orientation='Landscape')

    def copy_reports_to_home_dir(self):
        """Copy generated reports to home directory when run in WebGUI mode."""
        curr_path = self.result_dir
        home_dir = os.path.expanduser("~")
        out_folder_name = "WebGui_Reports"
        new_path = os.path.join(home_dir, out_folder_name)
        # webgui directory creation
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        test_name = self.test_name
        test_name_dir = os.path.join(new_path, test_name)
        # in webgui-reports DIR creating a directory with test name
        if not os.path.exists(test_name_dir):
            os.makedirs(test_name_dir)
        shutil.copytree(curr_path, test_name_dir, dirs_exist_ok=True)

    def webgui_finalize(self):
        """Test report finalization run when in WebGUI mode."""
        last_entry = self.overall[len(self.overall) - 1]
        last_entry["status"] = "Stopped"
        last_entry["timestamp"] = self.get_time_stamp_local()
        last_entry["end_time"] = self.get_time_stamp_local()
        self.overall.append(last_entry)

        df1 = pd.DataFrame(self.overall)
        df1.to_csv('{}/overall_multicast_throughput.csv'.format(self.result_dir), index=False)

        self.copy_reports_to_home_dir()


# Only used by argparser, so safe to exit in this function
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


def configure_reporting(local_lf_report_dir: str,
                        results_dir_name: str,
                        csv_outfile: str,
                        test_rig: str,
                        test_tag: str,
                        dut_hw_version: str,
                        dut_sw_version: str,
                        dut_model_num: str,
                        dut_serial_num: str,
                        test_id: str,
                        **kwargs):
    """Configure reporting, including report object and KPI CSV."""
    # Configure report
    #
    # Reporting needs to be in same directory when running w/ test framework (lf_check.py)
    if local_lf_report_dir != "":
        report = lf_report.lf_report(
            _path=local_lf_report_dir,
            _results_dir_name=results_dir_name,
            _output_html=f"{results_dir_name}.html",
            _output_pdf=f"{results_dir_name}.pdf")
    else:
        report = lf_report.lf_report(
            _results_dir_name=results_dir_name,
            _output_html=f"{results_dir_name}.html",
            _output_pdf=f"{results_dir_name}.pdf")

    # Configure report title banner
    #
    # Done outside of test class, as other test scripts currently use the
    # test class and will configure a different title
    report.set_title("Test Layer 3 Cross-Connect Traffic: test_l3.py ")
    report.build_banner_left()
    report.start_content_div2()

    # Configure KPI CSV. Output located in same directory as report
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

    if csv_outfile is not None:
        current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        csv_outfile = "{}_{}-test_l3.csv".format(
            csv_outfile, current_time)
        csv_outfile = report.file_add_path(csv_outfile)
        logger.info("csv output file : {}".format(csv_outfile))

    return report, kpi_csv, csv_outfile


def parse_args():
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

        # Interopt example Creating stations
            Interopt testing creating stations
            ./test_l3.py --lfmgr 192.168.0.103\
             --test_duration 60s\
            --polling_interval 5s\
            --upstream_port 1.1.eth2\
            --radio 'radio==wiphy4,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --radio 'radio==wiphy5,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --radio 'radio==wiphy6,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --radio 'radio==wiphy7,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --endp_type lf_udp,lf_tcp,mc_udp\
            --rates_are_totals\
            --side_a_min_bps=2000000\
            --side_b_min_bps=3000000\
            --test_rig CT-ID-004\
            --test_tag test_l3\
            --dut_model_num AXE11000\
            --dut_sw_version 3.0.0.4.386_44266\
            --dut_hw_version 1.0\
            --dut_serial_num 123456\
            --tos BX,BE,VI,VO\
            --log_level info\
            --no_cleanup\
            --cleanup_cx


            ./test_l3.py --lfmgr 192.168.0.103\
            --local_lf_report_dir /home/lanforge/html-reports/ct_id_004\
            --test_duration 30s\
            --polling_interval 5s\
            --upstream_port 1.1.eth2\
            --radio 'radio==wiphy4,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --radio 'radio==wiphy5,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --radio 'radio==wiphy6,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --radio 'radio==wiphy7,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down'\
            --endp_type lf_udp,lf_tcp,mc_udp\
            --side_a_min_bps=1000000\
            --side_b_min_bps=0\
            --side_a_min_pdu MTU\
            --side_b_min_pdu MTU\
            --test_rig CT-US-001\
            --test_tag 'TEST_L3_LONGEVITY_ENABLE_FLAGS_2G_W4_W5_W6_W7'\
            --dut_model_num ASUSRT-AX88U\
            --dut_sw_version 3.0.0.4.386_44266\
            --dut_hw_version 1.0\
            --dut_serial_num 12345678


        # Interopt using existing stations
            Interopt testing creating stations
            ./test_l3.py --lfmgr 192.168.91.50\
             --test_duration 60s\
            --polling_interval 5s\
            --upstream_port 1.50.eth2\
            --radio radio==wiphy1,stations==2,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable\
            --radio radio==wiphy4,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable\
            --radio radio==wiphy5,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable\
            --radio radio==wiphy6,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable\
            --radio radio==wiphy7,stations==1,ssid==axe11000_5g,ssid_pw==lf_axe11000_5g,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==ht160_enable&&wpa2_enable\
            --endp_type lf_udp,lf_tcp,mc_udp\
            --rates_are_totals\
            --side_a_min_bps=2000000\
            --side_b_min_bps=3000000\
            --test_rig CT-ID-004\
            --test_tag test_l3\
            --dut_model_num AXE11000\
            --dut_sw_version 3.0.0.4.386_44266\
            --dut_hw_version 1.0\
            --dut_serial_num 123456\
            --tos BX,BE,VI,VO\
            --log_level info\
            --no_cleanup\
            --cleanup_cx


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
             --radio 'radio==1.1.wiphy0,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy1,stations==1,ssid==Netgear5g,ssid_pw==lanforge,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy2,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,\
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000
             --test_rig ID_003 --test_tag 'l3_longevity' --dut_model_num GT-AXE11000 --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0 --dut_serial_num 12345678 --log_level debug

         # Setting wifi_settings per radio
            ./test_l3.py
            --lfmgr 192.168.100.116
            --local_lf_report_dir /home/lanforge/html-reports/
            --test_duration 15s
            --polling_interval 5s
            --upstream_port eth2
            --radio "radio==wiphy1,stations==4,ssid==asus11ax-5,ssid_pw==hello123,security==wpa2,
wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down&&ht160_enable)"
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
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Disabled'
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
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Disabled'
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
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Required'
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
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,\
wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Required'
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

        # Example : Wifi 7  6G LAN-4069

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
    Input       : Enum Val  : for list ,  telnet <mgr> 4001  , help add_profile

    Wifi_Mode
    Input       : Enum Val  : Shown by nc_show_ports
    <pre options='wifi_mode'>
    AUTO        |  0        #  Best Available
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
    abgn7       | 16        #  802.11abgn-EHT
                            #     a/b/g/n/AC/AX/EHT (dual-band AX) support
    bgn7        | 17        #  802.11bgn-EHT
    an7         | 18        #  802.11an-EHT
    a7          | 19        #  802.11a-EHT (6E disables /n and /ac)



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

    test_l3_parser.add_argument('--interopt_mode',
                                help="For Interopt continue to try running even if some clients do not get an IP.",
                                action='store_true')

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
        help='''--downstream_port <cross connect downstream_port>  for use when downstream is ethernet
        (eth to eth connection) do not use with wifi stations example: --downstream_port eth2''',
        default=None)
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
        '--upload_min_bps',
        dest='side_a_min_bps',
        help='''--side_a_min_bps, requested downstream min tx rate at stations / client, comma separated list for multiple iterations.  Default 0
                When running with tcp/udp traffic along with mcast , mcast will ignore the upload value''',
        default="0")
    test_l3_parser.add_argument(
        '-amp',
        '--side_a_min_pdu',
        help='--side_a_min_pdu, downstream pdu size, comma separated list for multiple iterations.  Default MTU',
        default="MTU")
    test_l3_parser.add_argument(
        '-bmr',
        '--download_min_bps',
        '--side_b_min_bps',
        '--do',
        dest='side_b_min_bps',
        help='''--side_b_min_bps or --download_min_bps, requested upstream min tx rate, comma separated list for multiple iterations.  Default 256000
                When runnign with tcp/udp and mcast will use this value''',
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
        help="Time (in seconds) to pause at end of test",
        type=int,
        default=0)

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

    test_l3_parser.add_argument(
        '--exit_on_ip_acquired', help='--exit_on_ip_acquired store true', action='store_true')

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
    # WebGUI argumemnts
    test_l3_parser.add_argument(
        '--dowebgui',
        help='--dowebgui True  if running through webgui',
        default=False)
    test_l3_parser.add_argument(
        '--test_name',
        help='Test name when running through webgui'
    )
    parser.add_argument('--help_summary',
                        default=None,
                        action="store_true",
                        help='Show summary of what this script does')

    return parser.parse_args()


# Starting point for running this from cmd line.
# note: when adding command line delimiters : +,=@
# https://stackoverflow.com/questions/37304799/cross-platform-safe-to-use-command-line-string-separator
#
# Safe to exit in this function, as this should only be called by this script
def main():
    endp_types = "lf_udp"

    help_summary = '''\
The Layer 3 Traffic Generation Test is designed to test the performance of the
Access Point by running layer 3 TCP and/or UDP Traffic.  Layer-3 Cross-Connects represent a stream
of data flowing through the system under test. A Cross-Connect (CX) is composed of two Endpoints,
each of which is associated with a particular Port (physical or virtual interface).

The test will create stations, create CX traffic between upstream port and stations, run traffic
and generate a report.
'''
    args = parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    test_name = ""
    ip = ""
    if args.dowebgui:
        logger.info("In webGUI execution")
        if args.dowebgui:
            test_name = args.test_name
            ip = args.lfmgr
            logger.info("dowebgui", args.dowebgui, test_name, ip)

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

    # Validate existing station list configuration if specified before starting test
    if not args.use_existing_station_list and args.existing_station_list:
        logger.error("Existing stations specified, but argument \'--use_existing_station_list\' not specified")
        exit(1)
    elif args.use_existing_station_list and not args.existing_station_list:
        logger.error(
            "Argument \'--use_existing_station_list\' specified, but no existing stations provided. See \'--existing_station_list\'")
        exit(1)

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

    # Configure reporting
    logger.info("Configuring report")
    report, kpi_csv, csv_outfile = configure_reporting(**vars(args))

    logger.debug("Configure test object")
    ip_var_test = L3VariableTime(
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
        interopt_mode=interopt_mode
    )

    # Perform pre-test cleanup, if configured to do so
    if args.no_pre_cleanup:
        logger.info("Skipping pre-test cleanup, '--no_pre_cleanup' specified")
    elif args.use_existing_station_list:
        logger.info("Skipping pre-test cleanup, '--use_existing_station_list' specified")
    else:
        logger.info("Performing pre-test cleanup")
        ip_var_test.pre_cleanup()

    # Build test configuration
    logger.info("Building test configuration")
    ip_var_test.build()
    if not ip_var_test.passes():
        logger.critical("Test configuration build failed")
        logger.critical(ip_var_test.get_fail_message())
        exit(1)

    # Run test
    logger.info("Starting test")
    ip_var_test.start(False)

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
            ip_var_test.quiesce_cx()
            time.sleep(3)
        else:
            logger.info("Test complete, stopping traffic")
            ip_var_test.stop()

    # Set DUT information for reporting
    ip_var_test.set_dut_info(
        dut_model_num=args.dut_model_num,
        dut_hw_version=args.dut_hw_version,
        dut_sw_version=args.dut_sw_version,
        dut_serial_num=args.dut_serial_num)
    ip_var_test.set_report_obj(report=report)

    # Generate and write out test report
    logger.info("Generating test report")
    ip_var_test.generate_report()
    ip_var_test.write_report()

    # TODO move to after reporting
    if not ip_var_test.passes():
        logger.warning("Test Ended: There were Failures")
        logger.warning(ip_var_test.get_fail_message())

    if args.no_cleanup:
        logger.info("Skipping post-test cleanup, '--no_cleanup' specified")
    elif args.no_stop_traffic:
        logger.info("Skipping post-test cleanup, '--no_stop_traffic' specified")
    else:
        logger.info("Performing post-test cleanup")
        ip_var_test.cleanup()

    # TODO: This is redundant if '--no_cleanup' is not specified (already taken care of there)
    if args.cleanup_cx:
        logger.info("Performing post-test CX traffic pair cleanup")
        ip_var_test.cleanup_cx()

    if ip_var_test.passes():
        test_passed = True
        logger.info("Full test passed, all connections increased rx bytes")

    # Run WebGUI-specific post test logic
    if args.dowebgui:
        ip_var_test.webgui_finalize()

    if test_passed:
        ip_var_test.exit_success()
    else:
        ip_var_test.exit_fail()


if __name__ == "__main__":
    main()
