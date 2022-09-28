#!/usr/bin/env python3
"""
NAME: lf_add_profile.py

PURPOSE:    Add LANforge device profile. This can give a high level description of how the LANforge system should act. 
            The profile can then be selected in higher-level test cases to auto-generate lower level configuration. 

EXAMPLE:


NOTES:


TO DO NOTES:

"""
import sys

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
from pprint import pformat
import os
import logging

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
from lanforge_client.lanforge_api import LFJsonQuery
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFSession


lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)

# add_wanpath
# http://www.candelatech.com/lfcli_ug.php#add_wanpath


class lf_add_profile():
    def __init__(self,
                 lf_mgr=None,
                 lf_port=None,
                 lf_user=None,
                 lf_passwd=None,
                 debug=False,
                 ):
        self.lf_mgr = lf_mgr
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_passwd = lf_passwd
        self.debug = debug

        self.session = LFSession(lfclient_url="http://%s:8080" % self.lf_mgr,
                                 debug=debug,
                                 connection_timeout_sec=4.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=True)
        # type hinting
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

    # http://www.candelatech.com/lfcli_ug.php#add_profile
    # add_profile Routed-AP-QA Routed-AP 0 4 0 0 vap hello123 4105
    def add_profile(self,
                    _alias_prefix: str = None,                 # Port alias prefix, aka hostname prefix.
                    _antenna: str = None,                      # Antenna count for this profile.
                    _bandwidth: str = None,                    # 0 (auto), 20, 40, 80 or 160
                    _eap_id: str = None,                       # EAP Identifier
                    _flags_mask: str = None,                   # Specify what flags to set.
                    _freq: str = None,                         # WiFi frequency to be used, 0 means default.
                    _instance_count: str = None,               # Number of devices (stations, vdevs, etc)
                    _mac_pattern: str = None,                  # Optional MAC-Address pattern, for instance:
                    # xx:xx:xx:*:*:xx
                    _name: str = None,                         # Profile Name. [R]
                    _passwd: str = None,                       # WiFi Password to be used (AP Mode), [BLANK] means no
                    # password.
                    _profile_flags: str = None,                # Flags for this profile, see above.
                    _profile_type: str = None,                 # Profile type: See above. [W]
                    _ssid: str = None,                         # WiFi SSID to be used, [BLANK] means any.
                    _vid: str = None,                          # Vlan-ID (only valid for vlan profiles).
                    _wifi_mode: str = None,                    # WiFi Mode for this profile.
                    _response_json_list: list = None,
                    _errors_warnings: list = None,
                    _suppress_related_commands: bool = False):

        self.command.post_add_profile(self, 
            alias_prefix=_alias_prefix,             # Port alias prefix, aka hostname prefix.
            antenna=_antenna,                       # Antenna count for this profile.
            bandwidth=_bandwidth,                   # 0 (auto), 20, 40, 80 or 160
            eap_id=_eap_id,                         # EAP Identifier
            flags_mask=_flags_mask,                 # Specify what flags to set.
            freq=_freq,                             # WiFi frequency to be used, 0 means default.
            instance_count=_instance_count,         # Number of devices (stations, vdevs, etc)
            mac_pattern=_mac_pattern,               # Optional MAC-Address pattern, for instance:
            # xx:xx:xx:*:*:xx
            name=_name,                             # Profile Name. [R]
            passwd=_passwd,                         # WiFi Password to be used (AP Mode), [BLANK] means no
            # password.
            profile_flags=_profile_flags,           # Flags for this profile, see above.
            profile_type=_profile_type,             # Profile type: See lanforge_api [W]
            ssid=_ssid,                             # WiFi SSID to be used, [BLANK] means any.
            vid=_vid,                               # Vlan-ID (only valid for vlan profiles).
            wifi_mode=_wifi_mode,                   # WiFi Mode for this profile.
            response_json_list=_response_json_list,
            debug=self.debug,
            errors_warnings=_errors_warnings,
            suppress_related_commands=_suppress_related_commands)

    # This text will be added to the end of the notes field for Profiles. 
    # The text must be entered one line at a time, primarily due to CLI parsing limitations. 

    # http://www.candelatech.com/lfcli_ug.php#add_profile_notes
    def add_profile_notes(
        dut: str = None,                          # Profile Name. [R]
        text: str = None,                         # [BLANK] will erase all, any other text will be
        # appended to existing text. <tt
        # escapearg='false'>Unescaped Value</tt>
        response_json_list: list = None,
        errors_warnings: list = None,
        suppress_related_commands: bool = False):

        self.command.post_add_profile_notes(
                               dut,                          # Profile Name. [R]
                               text,                         # [BLANK] will erase all, any other text will be
                               # appended to existing text. <tt
                               # escapearg='false'>Unescaped Value</tt>
                               response_json_list,
                               debug=self.debug,
                               errors_warnings=_error_warnings,
                               suppress_related_commands=_suppress_related_commands)



# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='''\
            adds a chamberview profile

            add_profile Routed-AP-QA Routed-AP 0 4 0 0 vap hello123 4105

            profile flags            

            ''')
    # http://www.candelatech.com/lfcli_ug.php#add_profile
    parser.add_argument("--host", "--mgr", dest='mgr', help='specify the GUI to connect to')
    parser.add_argument("--mgr_port", help="specify the GUI to connect to, default 8080", default="8080")
    parser.add_argument("--lf_user", help="specify the GUI to connect to, default 8080", default="lanforge")
    parser.add_argument("--lf_passwd", help="specify the GUI to connect to, default 8080", default="lanforge")

    # http://www.candelatech.com/lfcli_ug.php#add_profile
    parser.add_argument('--alias_prefix', dest='(add profile) alias_prefix', help='Port alias prefix, aka hostname prefix. ')
    parser.add_argument('--antenna', help="(add profile) Antenna count for this profile.")
    parser.add_argument('--bandwidth', help="(add profile) 0 (auto), 20, 40, 80 or 160")
    parser.add_argument("--eap_id", help="(add profile) EAP Identifier")
    parser.add_argument("--flags_mask", help="(add profile) Specify what flags to set.")
    parser.add_argument("--freq", help="(add profile)WiFi frequency to be used, 0 means default.")
    parser.add_argument("--instance_count", help="(add profile) Number of devices (stations, vdevs, etc)")
    parser.add_argument("--mac_pattern", help="(add profile) Optional MAC-Address pattern, for instance:  xx:xx:xx:*:*:xx")
    parser.add_argument("--name", help="(add profile) Profile Name. [R] ", required=True)
    parser.add_argument('--passwd', help='(add profile) WiFi SSID to be used, [BLANK] means any.')
    parser.add_argument('--profile_flags', help=''' 
                                    (add profile) Flags for this profilelanforge_api AddProfileProfileFlags'
                                    enter the flags as a list 0x1009 is:
                                        DHCP_SERVER = 0x1           # This should provide DHCP server.
                                        SKIP_DHCP_ROAM = 0x10       # Ask station to not re-do DHCP on roam.
                                        NAT = 0x100                 # Enable NAT if this object is in a virtual router
                                        ENABLE_POWERSAVE = 0x1000   # Enable power-save when creating stations.

                                        pass in --profile_flags 'DHCP_SERVER,SKIP_DHCP_ROAM,NAT,ENABLE_POWERSAVE'

                                    flags:
                                            p_11r = 0x40                   # Use 802.11r roaming setup.
                                            ALLOW_11W = 0x800              # Set 11w (MFP/PMF) to optional.
                                            BSS_TRANS = 0x400              # Enable BSS Transition logic
                                            DHCP_SERVER = 0x1              # This should provide DHCP server.
                                            EAP_PEAP = 0x200               # Enable EAP-PEAP
                                            EAP_TTLS = 0x80                # Use 802.1x EAP-TTLS
                                            ENABLE_POWERSAVE = 0x1000      # Enable power-save when creating stations.
                                            NAT = 0x100                    # Enable NAT if this object is in a virtual router
                                            SKIP_DHCP_ROAM = 0x10          # Ask station to not re-do DHCP on roam.
                                            WEP = 0x2                      # Use WEP encryption
                                            WPA = 0x4                      # Use WPA encryption
                                            WPA2 = 0x8                     # Use WPA2 encryption
                                            WPA3 = 0x20                    # Use WPA3 encryption
                                    ''')
    parser.add_argument("--profile_type", help='''(add profile) Profile type: [W]
                                                Bridged_AP: briged-AP
                                                Monitor: monitor
                                                Peer: peer
                                                RDD: rdd
                                                Routed_AP: routed-AP
                                                STA: STA-AC
                                                STA: STA-AUTO
                                                STA: STA-AX
                                                STA: STA-abg
                                                STA: STA-n
                                                Uplink: uplink-nat
                                                Upstream: upstrream
                                                Upstream: upstream-dhcp
                                                as_is: as-is
                                                NA
                                                ''')
    parser.add_argument("--ssid", help='(add profile) WiFi SSID to be used, [BLANK] means any.')
    parser.add_argument("--vid", help='(add profile) Vlan-ID (only valid for vlan profiles).')
    parser.add_argument("--wifi_mode", help='''(add profile) WiFi Mode for this profile.
        p_802_11a = "802.11a"        # 802.11a
        AUTO = "AUTO"                # 802.11g
        aAX = "aAX"                  # 802.11a-AX (6E disables /n and /ac)
        abg = "abg"                  # 802.11abg
        abgn = "abgn"                # 802.11abgn
        abgnAC = "abgnAC"            # 802.11abgn-AC
        abgnAX = "abgnAX"            # 802.11abgn-AX
        an = "an"                    # 802.11an
        anAC = "anAC"                # 802.11an-AC
        anAX = "anAX"                # 802.11an-AX
        as_is = "as_is"              # Make no changes to current configuration
        b = "b"                      # 802.11b
        bg = "bg"                    # 802.11bg
        bgn = "bgn"                  # 802.11bgn
        bgnAC = "bgnAC"              # 802.11bgn-AC
        bgnAX = "bgnAX"              # 802.11bgn-AX
        bond = "bond"                # Bonded pair of Ethernet ports.
        bridged_ap = "bridged_ap"    # AP device in bridged mode. The EIDs may specify radio and bridged port.
        client = "client"            # Client-side non-WiFi device (Ethernet port, for instance).
        g = "g"                      # 802.11g
        mobile_sta = "mobile_sta"    # Mobile station device. Expects to connect to DUT AP(s) and upstream LANforge.
        monitor = "monitor"          # Monitor device/sniffer. The EIDs may specify which radios to use.
        peer = "peer"                # Edge device, client or server (Ethernet port, for instance).
        rdd = "rdd"                  # Pair of redirect devices, typically associated with VR to act as traffic endpoint
        routed_ap = "routed_ap"      # AP in routed mode. The EIDs may specify radio and upstream port.
        sta = "sta"                  # Station device, most likely non mobile. The EIDs may specify radio(s) to use
        uplink = "uplink"            # Uplink towards rest of network (can go in virtual router and do NAT)
        upstream = "upstream"        # Upstream server device. The EIDs may specify which ports to use.
        vlan = "vlan"                # 802.1q VLAN. Specify VID with the 'freq' option.
        ''')

    # http://www.candelatech.com/lfcli_ug.php#add_profile_notes
    parser.add_argument('--dut', help='(add profile notes) Profile Name. [R]', required=True)
    parser.add_argument('--text', help='(add profile notes) [BLANK] will erase all, any other text will be  appended to existing text. must be entered line by line')

    # Logging Configuration
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--debug', help='Legacy debug flag', action='store_true')

    args = parser.parse_args()

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

    if not args.wl_name:
        logger.error("No wanlink name provided")
        exit(1)

    wanlink = lf_add_profile(lf_mgr=args.mgr,
                            lf_port=8080,
                            lf_user=args.lf_user,
                            lf_passwd=args.lf_passwd,
                            debug=True)

    # parameters for add_profile
    # alias
    endp_A = args.wl_name + "-A"
    endp_B = args.wl_name + "-B"

    latency_A = args.latency_A if args.latency_A is not None else args.latency
    latency_B = args.latency_B if args.latency_B is not None else args.latency

    max_rate_A = args.max_rate_A if args.max_rate_A is not None else args.max_rate
    max_rate_B = args.max_rate_B if args.max_rate_B is not None else args.max_rate

    # parameters for set_wanlink_info
    drop_freq_A = args.drop_freq_A if args.drop_freq_A is not None else args.drop_freq
    drop_freq_B = args.drop_freq_B if args.drop_freq_B is not None else args.drop_freq

    dup_freq_A = args.dup_freq_A if args.dup_freq_A is not None else args.dup_freq
    dup_freq_B = args.dup_freq_B if args.dup_freq_B is not None else args.dup_freq

    extra_buffer_A = args.extra_buffer_A if args.extra_buffer_A is not None else args.extra_buffer
    extra_buffer_B = args.extra_buffer_B if args.extra_buffer_B is not None else args.extra_buffer

    jitter_freq_A = args.jitter_freq_A if args.jitter_freq_A is not None else args.jitter_freq
    jitter_freq_B = args.jitter_freq_B if args.jitter_freq_B is not None else args.jitter_freq

    latency_packet_A = args.latency_packet_A if args.latency_packet_A is not None else args.latency_packet
    latency_packet_B = args.latency_packet_B if args.latency_packet_B is not None else args.latency_packet

    max_drop_amt_A = args.max_drop_amt_A if args.max_drop_amt_A is not None else args.max_drop_amt
    max_drop_amt_B = args.max_drop_amt_B if args.max_drop_amt_B is not None else args.max_drop_amt

    max_jitter_A = args.max_jitter_A if args.max_jitter_A is not None else args.max_jitter
    max_jitter_B = args.max_jitter_B if args.max_jitter_B is not None else args.max_jitter

    max_lateness_A = args.max_lateness_A if args.max_lateness_A is not None else args.max_lateness
    max_lateness_B = args.max_lateness_B if args.max_lateness_B is not None else args.max_lateness

    max_reorder_amt_A = args.max_reorder_amt_A if args.max_reorder_amt_A is not None else args.max_reorder_amt
    max_reorder_amt_B = args.max_reorder_amt_B if args.max_reorder_amt_B is not None else args.max_reorder_amt

    min_drop_amt_A = args.min_drop_amt_A if args.min_drop_amt_A is not None else args.min_drop_amt
    min_drop_amt_B = args.min_drop_amt_B if args.min_drop_amt_B is not None else args.min_drop_amt

    min_reorder_amt_A = args.min_reorder_amt_A if args.min_reorder_amt_A is not None else args.min_reorder_amt
    min_reorder_amt_B = args.min_reorder_amt_B if args.min_reorder_amt_B is not None else args.min_reorder_amt

    reorder_freq_A = args.reorder_freq_A if args.reorder_freq_A is not None else args.reorder_freq
    reorder_freq_B = args.reorder_freq_B if args.reorder_freq_B is not None else args.reorder_freq

    speed_A = args.speed_A if args.speed_A is not None else args.speed
    speed_B = args.speed_B if args.speed_B is not None else args.speed

    # Comment out some parameters like 'max_jitter', 'drop_freq' and 'wanlink'
    # in order to view the X-Errors headers

    # create side A
    wanlink.add_wl_endp(_alias=endp_A,                        # Name of endpoint. [R]
                        _cpu_id=args.cpu_id,                  # The CPU/thread that this process should run on (kernel-mode only).
                        _description=args.description,        # Description for this endpoint, put in single quotes if it contains spaces.
                        _latency=latency_A,                   # The latency (ms) that will be added to each packet entering this WanLink.
                        _max_rate=max_rate_A,                 # Maximum transmit rate (bps) for this WanLink.
                        _port=args.port_A,                    # Port number. [W]
                        _resource=args.resource,              # Resource number. [W]
                        _shelf=args.shelf,                    # Shelf name/id. [R][D:1]
                        _wle_flags=args.wle_flags,            # WanLink Endpoint specific flags, see above.
                        _suppress_related_commands=args.suppress_related_commands)

    # endp B
    wanlink.add_wl_endp(_alias=endp_B,                        # Name of endpoint. [R]
                        _cpu_id=args.cpu_id,                  # The CPU/thread that this process should run on (kernel-mode only).
                        _description=args.description,        # Description for this endpoint, put in single quotes if it contains spaces.
                        _latency=latency_B,                   # The latency (ms) that will be added to each packet entering this WanLink.
                        _max_rate=max_rate_B,                 # Maximum transmit rate (bps) for this WanLink.
                        _port=args.port_B,                    # Port number. [W]
                        _resource=args.resource,              # Resource number. [W]
                        _shelf=args.shelf,                    # Shelf name/id. [R][D:1]
                        _wle_flags=args.wle_flags,            # WanLink Endpoint specific flags, see above.
                        _suppress_related_commands=args.suppress_related_commands)

    result = wanlink.add_cx(_alias=args.wl_name,
                            _rx_endp=endp_A,
                            _tx_endp=endp_B,
                            _test_mgr="default_tm")

    logger.debug(pformat(result))

    # set_wanlink_info A
    wanlink.set_wanlink_info(_drop_freq=drop_freq_A,                    # How often, out of 1,000,000 packets, should we
                             # purposefully drop a packet.
                             _dup_freq=dup_freq_A,                     # How often, out of 1,000,000 packets, should we
                             # purposefully duplicate a packet.
                             _extra_buffer=extra_buffer_A,                 # The extra amount of bytes to buffer before
                             # dropping pkts, in units of 1024. Use -1 for AUTO.
                             _jitter_freq=jitter_freq_A,                  # How often, out of 1,000,000 packets, should we
                             # apply jitter.
                             _latency=latency_packet_A,                      # The base latency added to all packets, in
                             # milliseconds (or add 'us' suffix for microseconds
                             _max_drop_amt=max_drop_amt_A,                 # Maximum amount of packets to drop in a row.
                             # Default is 1.
                             _max_jitter=max_jitter_A,                   # The maximum jitter, in milliseconds (or ad 'us'
                             # suffix for microseconds)
                             _max_lateness=max_lateness_A,                 # Maximum amount of un-intentional delay before pkt
                             # is dropped. Default is AUTO
                             _max_reorder_amt=max_reorder_amt_A,              # Maximum amount of packets by which to reorder,
                             # Default is 10.
                             _min_drop_amt=min_drop_amt_A,                 # Minimum amount of packets to drop in a row.
                             # Default is 1.
                             _min_reorder_amt=min_reorder_amt_A,              # Minimum amount of packets by which to reorder,
                             # Default is 1.
                             _name=endp_A,                         # The name of the endpoint we are configuring. [R]
                             _playback_capture_file=args.playback_capture_file,        # Name of the WAN capture file to play back.
                             _reorder_freq=reorder_freq_A,                 # How often, out of 1,000,000 packets, should we
                             # make a packet out of order.
                             _speed=speed_A,                        # The maximum speed of traffic this endpoint will
                             # accept (bps).
                             _debug=args.debug,
                             _suppress_related_commands=args.suppress_related_commands)

    if args.kernel_mode:
        wanlink.set_endp_flag(_name=endp_A,
                            _flag=wanlink.command.SetEndpFlagFlag.KernelMode.value,
                            _val=1,
                            _suppress_related_commands=args.suppress_related_commands)

    else:                                
        wanlink.set_endp_flag(_name=endp_A,
                            _flag=wanlink.command.SetEndpFlagFlag.KernelMode.value,
                            _val=0,
                            _suppress_related_commands=args.suppress_related_commands)

    if args.pass_through_mode:
        wanlink.set_endp_flag(_name=endp_A,
                            _flag='PassthroughMode',
                            _val=1,
                            _suppress_related_commands=args.suppress_related_commands)

    else:                                
        wanlink.set_endp_flag(_name=endp_A,
                            _flag='PassthroughMode',
                            _val=0,
                            _suppress_related_commands=args.suppress_related_commands)


    # set_wanlink_info B
    wanlink.set_wanlink_info(_drop_freq=drop_freq_B,                    # How often, out of 1,000,000 packets, should we
                             # purposefully drop a packet.
                             _dup_freq=dup_freq_B,                     # How often, out of 1,000,000 packets, should we
                             # purposefully duplicate a packet.
                             _extra_buffer=extra_buffer_B,                 # The extra amount of bytes to buffer before
                             # dropping pkts, in units of 1024. Use -1 for AUTO.
                             _jitter_freq=jitter_freq_B,                  # How often, out of 1,000,000 packets, should we
                             # apply jitter.
                             _latency=latency_packet_B,                      # The base latency added to all packets, in
                             # milliseconds (or add 'us' suffix for microseconds
                             _max_drop_amt=max_drop_amt_B,                 # Maximum amount of packets to drop in a row.
                             # Default is 1.
                             _max_jitter=max_jitter_B,                   # The maximum jitter, in milliseconds (or ad 'us'
                             # suffix for microseconds)
                             _max_lateness=max_lateness_B,                 # Maximum amount of un-intentional delay before pkt
                             # is dropped. Default is AUTO
                             _max_reorder_amt=max_reorder_amt_B,              # Maximum amount of packets by which to reorder,
                             # Default is 10.
                             _min_drop_amt=min_drop_amt_B,                 # Minimum amount of packets to drop in a row.
                             # Default is 1.
                             _min_reorder_amt=min_reorder_amt_B,              # Minimum amount of packets by which to reorder,
                             # Default is 1.
                             _name=endp_B,                         # The name of the endpoint we are configuring. [R]
                             _playback_capture_file=args.playback_capture_file,        # Name of the WAN capture file to play back.
                             _reorder_freq=reorder_freq_B,                 # How often, out of 1,000,000 packets, should we
                             # make a packet out of order.
                             _speed=speed_B,                        # The maximum speed of traffic this endpoint will
                             # accept (bps).
                             _debug=args.debug,
                             _suppress_related_commands=args.suppress_related_commands)

    if args.kernel_mode:
        wanlink.set_endp_flag(_name=endp_B,
                            _flag=wanlink.command.SetEndpFlagFlag.KernelMode.value,
                            _val=1,
                            _suppress_related_commands=args.suppress_related_commands)

    else:                                
        wanlink.set_endp_flag(_name=endp_B,
                            _flag=wanlink.command.SetEndpFlagFlag.KernelMode.value,
                            _val=0,
                            _suppress_related_commands=args.suppress_related_commands)
    if args.pass_through_mode:
        wanlink.set_endp_flag(_name=endp_B,
                            _flag='PassthroughMode',
                            _val=1,
                            _suppress_related_commands=args.suppress_related_commands)

    else:                                
        wanlink.set_endp_flag(_name=endp_B,
                            _flag='PassthroughMode',
                            _val=0,
                            _suppress_related_commands=args.suppress_related_commands)


    eid_list = [args.wl_name]
    ewarn_list = []
    result = wanlink.get_wl(_eid_list=eid_list,
                            _wait_sec=0.2,
                            _timeout_sec=2.0,
                            _errors_warnings=ewarn_list)
    logger.debug(pformat(result))

    eid_list = [endp_A, endp_B]
    result = wanlink.get_wl_endp(_eid_list=eid_list,
                            _wait_sec=0.2,
                            _timeout_sec=2.0,
                            _errors_warnings=ewarn_list)
    logger.debug(pformat(result))



if __name__ == "__main__":
    main()
