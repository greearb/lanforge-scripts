#!/usr/bin/env python3
r"""
NAME:       create_station.py

PURPOSE:    Create and configure one or more of WiFi stations ports using the
            specified parent radio.

NOTES:      This script is intended to only create and configure stations. See other scripts
            like 'test_l3.py' to create and run tests.

            By default, the script will also attempt to connect the WiFi stations as configured
            unless the '--create_admin_down' argument is specified.

            --mode <mode_num>
                Set the station WiFi mode (e.g. to configure a 802.11be radio as 802.11ax)
                See the 'add_sta' command's mode option in the CLI documentation for
                available mode settings. Link here: http://www.candelatech.com/lfcli_ug.php#add_sta

            --station_flags  <station_flags>
                Comma-separated list of flags to configure the station with (e.g. 'ht160_enable,disable_sgi'
                to enable 160MHz channel usage and disable 802.11ac short guard interval (SGI), respectively).
                Note that other options like '--security' configure authentication-based station flags.
                See the 'add_sta' command's 'flags' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#add_sta

            --country_code 840
                United States   :   840     |       Dominican Rep   :   214     |      Japan (JE2)     :   397     |      Portugal        :   620
                Albania         :   8       |       Ecuador         :   218     |      Jordan          :   400     |      Pueto Rico      :   630
                Algeria         :   12      |       Egypt           :   818     |      Kazakhstan      :   398     |      Qatar           :   634
                Argentina       :   32      |       El Salvador     :   222     |      North Korea     :   408     |      Romania         :   642
                Bangladesh      :   50      |       Estonia         :   233     |      South Korea     :   410     |      Russia          :   643
                Armenia         :   51      |       Finland         :   246     |      South Korea     :   411     |      Saudi Arabia    :   682
                Australia       :   36      |       France          :   250     |      Kuwait          :   414     |      Singapore       :   702
                Austria         :   40      |       Georgia         :   268     |      Latvia          :   428     |      Slovak Republic :   703
                Azerbaijan      :   31      |       Germany         :   276     |      Lebanon         :   422     |      Slovenia        :   705
                Bahrain         :   48      |       Greece          :   300     |      Liechtenstein   :   438     |      South Africa    :   710
                Barbados        :   52      |       Guatemala       :   320     |      Lithuania       :   440     |      Spain           :   724
                Belarus         :   112     |       Haiti           :   332     |      Luxembourg      :   442     |      Sweden          :   752
                Belgium         :   56      |       Honduras        :   340     |      Macau           :   446     |      Switzerland     :   756
                Belize          :   84      |       Hong Kong       :   344     |      Macedonia       :   807     |      Syria           :   760
                Bolivia         :   68      |       Hungary         :   348     |      Malaysia        :   458     |      Taiwan          :   158
                BiH             :   70      |       Iceland         :   352     |      Mexico          :   484     |      Thailand        :   764
                Brazil          :   76      |       India           :   356     |      Monaco          :   492     |      Trinidad &Tobago:   780
                Brunei          :   96      |       Indonesia       :   360     |      Morocco         :   504     |      Tunisia         :   788
                Bulgaria        :   100     |       Iran            :   364     |      Netherlands     :   528     |      Turkey          :   792
                Canada          :   124     |       Ireland         :   372     |      Aruba           :   533     |      U.A.E.          :   784
                Chile           :   152     |       Israel          :   376     |      New Zealand     :   554     |      Ukraine         :   804
                China           :   156     |       Italy           :   380     |      Norway          :   578     |      United Kingdom  :   826
                Colombia        :   170     |       Jamaica         :   388     |      Oman            :   512     |      Uruguay         :   858
                Costa Rica      :   188     |       Japan           :   392     |      Pakistan        :   586     |      Uzbekistan      :   860
                Croatia         :   191     |       Japan (JP1)     :   393     |      Panama          :   591     |      Venezuela       :   862
                Cyprus          :   196     |       Japan (JP0)     :   394     |      Peru            :   604     |      Vietnam         :   704
                Czech Rep       :   203     |       Japan (JP1-1)   :   395     |      Philippines     :   608     |      Yemen           :   887
                Denmark         :   208     |       Japan (JE1)     :   396     |      Poland          :   616     |      Zimbabwe        :   716

            --no_pre_cleanup
                Disables station cleanup before creation of stations. Default behavior will remove any existing stations.

            --cleanup
                Add this flag to clean up stations after creation

            --eap_method <eap_method>
                EAP method used by station in authentication.
                See the 'set_wifi_extra' command's 'eap' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#set_wifi_extra

            --key_mgmt <protocol>
                Key management protocol used by the station in authentication.

            --pairwise_cipher <cipher>
                Pairwise cipher used by station in authentication.
                See the 'set_wifi_extra' command's 'pairwise' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#set_wifi_extra

            --groupwise_cipher <cipher>
                Groupwise cipher used by station in authentication.
                See the 'set_wifi_extra' command's 'groupwise' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#set_wifi_extra

            --eap_identity <eap_identity>
                EAP identity (i.e. username) used by the station in authentication.

            --eap_password <eap_password>
                EAP password used by the station in authentication.

            --pk_passwd <password>
                Private key password used by the station in authentication. Required for TLS-based authentication.

            --ca_cert <path_to_certificate>
                Path to Certificate authority certificate used by the station in authentication.
                Required for TLS-based authentication.
                Note this is the path on the LANforge system where this station will be created.

            --private_key <path_to_private_key>
                Path to private key used by the station in authentication. Required for TLS-based authentication.
                Note this is the path on the LANforge system where this station will be created.

EXAMPLE:
            # Create a single station
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --passwd    <password> \
                   --security  wpa2

            # Create multiple stations with initial band preference 5G
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --passwd    <password> \
                   --security  wpa2 \
                   --num_stations 10 \
                   --initial_band_pref 5G

            # Create multiple stations
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --num_stations  10

            # Create a multiple stations, all associated to specific BSSID
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --bssid     <bssid> \
                   --passwd    <password> \
                   --security  wpa2

            # Create a multiple stations with specific numbering scheme
            # In this example, create five stations with names of the format: "sta1000", "sta1001", "sta1002", etc.
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --start_id      1000 \
                   --num_stations  5

            # Create a station, configuring radio settings like antenna, channel, etc.
            # In this example, configure radio to use antennas (2x2 station) and channel 6
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --radio_antenna 2 \
                   --radio_channel 6

            # Create a station, configuring the station to be a specific WiFi mode
            # (e.g. configuring an 802.11ax-capable radio to create an 802.11ac station)
            # See the 'add_sta' command's mode option in the CLI documentation for
            # available mode settings. Link here: http://www.candelatech.com/lfcli_ug.php#add_sta
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --passwd    <password> \
                   --security  wpa2 \
                   --mode      6

            # Create a station, configuring specific station flags
            # In this example, enable 160MHz channels and disable 802.11ac short guard interval (SGI).
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --radio_antenna 2 \
                   --radio_channel 6 \
                   --station_flags "ht160_enable,disable_sgi"

            # Create a station using TLS-based enterprise authentication
            # Note that paths are paths on the LANforge system where the station will be created.
               ./create_station.py \
                   --mgr               <lanforge ip> \
                   --radio             1.1.wiphy1 \
                   --ssid              <ssid> \
                   --security          <wpa2|wpa3> \
                   --key_mgmt          <key_mgmt> \
                   --pairwise_cipher   <cipher> \
                   --groupwise_cipher  <cipher> \
                   --eap_method        TLS \
                   --eap_identity      <username> \
                   --eap_password      <password> \
                   --pk_passwd         <password> \
                   --private_key       <path> \
                   --ca_cert           <path>

            # Create a station using TTLS-based enterprise authentication
               ./create_station.py \
                   --mgr               <lanforge ip> \
                   --radio             1.1.wiphy1 \
                   --ssid              <ssid> \
                   --security          <wpa2|wpa3> \
                   --key_mgmt          <TTLS|PEAP> \
                   --pairwise_cipher   <cipher> \
                   --groupwise_cipher  <cipher> \
                   --eap_method        TTLS \
                   --eap_identity      <username> \
                   --eap_password      <password>

            #    Create station specifying a custom 'wpa_supplicant' config command
            #    In this example, specify a background scanning 'wpa_supplicant' command, useful for roaming.
            #    Here, the background scan is configured to a threshold of -65 dBm RSSI with a short and long interval of 50 and 300 seconds.
            #    See 'man wpa_supplicant.conf' for more information.
                ./create_station.py \
                    --mgr               <lanforge ip> \
                    --radio             1.1.wiphy1 \
                    --ssid              <ssid> \
                    --passwd            <password> \
                    --security          wpa2 \
                    --custom_wifi_cmd   'bgscan="simple:50:-65:300"'

SCRIPT_CLASSIFICATION:
            Creation

SCRIPT_CATEGORIES:
            Functional

STATUS:     Functional

VERIFIED_ON:
            9-JUN-2023,
            GUI Version:  5.4.6
            Kernel Version: 5.19.17+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README:
            False
"""
import sys
import os
import importlib
import argparse
import pprint
import logging

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
lf_modify_radio = importlib.import_module("py-scripts.lf_modify_radio")
add_sta = importlib.import_module("py-json.LANforge.add_sta")


class CreateStation(Realm):
    # Map values displayed in GUI to values accepted by the server
    # Key is value displayed in GUI, value is value accepted by server
    EAP_METHOD_MAP = {
        "DEFAULT": "DEFAULT",
        "EAP-MD5": "MD5",
        "MSCHAPV2": "MSCHAPV2",
        "EAP-OTP": "OTP",
        "EAP-GTC": "GTC",
        "EAP-TLS": "TLS",
        "EAP-PEAP": "PEAP",
        "EAP-TTLS": "TTLS",
        "EAP-SIM": "SIM",
        "EAP-AKA": "AKA",
        "EAP-PSK": "PSK",
        "EAP-IKEV2": "IKEV2",
        "EAP-FAST": "FAST",
        "WFA-UNAUTH-TLS": "WFA-UNAUTH-TLS",
        "TTLS PEAP TLS": "TTLS PEAP TLS",
    }

    KEY_MGMT_MAP = {
        "DEFAULT": "DEFAULT",
        "NONE": "NONE",
        "WPA-PSK": "WPA-PSK",
        "FT-PSK (11r)": "FT-PSK",
        "FT-EAP (11r)": "FT-EAP",
        "FT-SAE (11r)": "FT-SAE",
        "FT-SAE-EXT-KEY (11r)": "FT-SAE-EXT-KEY",
        "FT-EAP-SHA384 (11r)": "FT-EAP-SHA-384",
        "WPA-EAP": "WPA-EAP",
        "OSEN": "OSEN",
        "IEEE8021X": "IEEE8021X",
        "WPA-PSK-SHA256": "WPA-PSK-SHA256",
        "WPA-EAP-SHA256": "WPA-EAP-SHA256",
        "PSK & EAP 128": "WPA-PSK WPA-EAP",
        "PSK & EAP 256": "WPA-PSK-256 WPA-EAP-256",
        "PSK & EAP 128/256": "WPA-PSK WPA-EAP WPA-PSK-256 WPA-EAP-256",
        "SAE": "SAE",
        "SAE-EXT-KEY": "SAE-EXT-KEY",
        "WPA-EAP-SUITE-B": "WPA-EAP-SUITE-B",
        "WPA-EAP-SUITE-B-192": "WPA-EAP-SUITE-B-192",
        "FILS-SHA256": "FILS-SHA256",
        "FILS-SHA384": "FILS-SHA384",
        "OWE": "OWE",
    }

    PAIRWISE_CIPHER_MAP = {
        "DEFAULT": "DEFAULT",
        "CCMP": "CCMP",
        "TKIP": "TKIP",
        "NONE": "NONE",
        "CCMP TKIP": "CCMP TKIP",
        "CCMP-256": "CCMP-256",
        "GCMP (wpa3)": "GCMP",
        "GCMP-256 (wpa3)": "GCMP-256",
        "CCMP/GCMP-256 (wpa3)": "GCMP-256 CCMP-256",
    }

    GROUPWISE_CIPHER_MAP = {
        "DEFAULT": "DEFAULT",
        "CCMP": "CCMP",
        "WEP104": "WEP104",
        "WEP40": "WEP40",
        "GTK_NOT_USED": "GTK_NOT_USED",
        "GCMP-256 (wpa3)": "GCMP-256",
        "CCMP-256 (wpa3)": "CCMP-256",
        "GCMP/CCMP-256 (wpa3)": "GCMP-256 CCMP-256",
        "All": "CCMP TKIP WEP104 WEP40 CCMP-256 GCMP-256",
    }

    def __init__(self,
                 mgr,
                 mgr_port,
                 proxy,
                 debug,
                 up,
                 radio,
                 ssid,
                 bssid,
                 mode,
                 sta_list,
                 station_flags,
                 mac_pattern,
                 security,
                 password,
                 eap_method,
                 eap_identity,
                 eap_anonymous_identity,
                 eap_password,
                 eap_phase1,
                 eap_phase2,
                 pk_passwd,
                 ca_cert,
                 private_key,
                 key_mgmt,
                 pairwise_cipher,
                 groupwise_cipher,
                 set_txo_data,
                 custom_wifi_cmd,
                 initial_band_pref,
                 **kwargs):
        super().__init__(mgr,
                         mgr_port)
        self.host = mgr
        self.port = mgr_port
        self.debug = debug
        self.up = up
        self.ssid = ssid
        self.bssid = bssid

        self.mode = mode
        if mode:
            if str.isalpha(mode):
                self.mode = add_sta.add_sta_modes[mode]

        self.sta_list = sta_list
        self.sta_flags = station_flags
        self.radio = radio
        self.timeout = 120
        self.security = security
        self.initial_band_pref = initial_band_pref
        self.password = password

        # Translate from options displayed in the GUI to options
        # that the server actually understands
        if eap_method in self.EAP_METHOD_MAP:
            self.eap_method = self.EAP_METHOD_MAP[eap_method]
        else:
            self.eap_method = eap_method

        self.eap_identity = eap_identity
        self.eap_anonymous_identity = eap_anonymous_identity
        self.eap_password = eap_password
        self.eap_phase1 = eap_phase1
        self.eap_phase2 = eap_phase2
        self.pk_passwd = pk_passwd
        self.ca_cert = ca_cert
        self.private_key = private_key

        # Translate from options displayed in the GUI to options
        # that the server actually understands
        if key_mgmt in self.KEY_MGMT_MAP:
            self.key_mgmt = self.KEY_MGMT_MAP[key_mgmt]
        else:
            self.key_mgmt = key_mgmt

        if pairwise_cipher in self.PAIRWISE_CIPHER_MAP:
            self.pairwise_cipher = self.PAIRWISE_CIPHER_MAP[pairwise_cipher]
        else:
            self.pairwise_cipher = pairwise_cipher

        if groupwise_cipher in self.GROUPWISE_CIPHER_MAP:
            self.groupwise_cipher = self.GROUPWISE_CIPHER_MAP[groupwise_cipher]
        else:
            self.groupwise_cipher = groupwise_cipher

        self.set_txo_data = set_txo_data
        self.custom_wifi_cmd = custom_wifi_cmd

        self.station_profile = self.new_station_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.bssid = self.bssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.mode = self.mode
        self.station_profile.set_command_param("add_sta", "mac", mac_pattern)

        if self.sta_flags is not None:
            _flags = self.sta_flags.split(',')
            for flags in _flags:
                logger.info(f"Selected Flags: '{flags}'")
                self.station_profile.set_command_flag("add_sta", flags, 1)

        logger.debug(pprint.pformat(self.sta_list))

    def cleanup(self):
        """Remove any conflicting LANforge port(s)."""
        for station in self.sta_list:
            logger.info('Removing the station {} if exists'.format(station))
            self.rm_port(station, check_exists=True)
        if (not LFUtils.wait_until_ports_disappear(base_url=self.station_profile.lfclient_url, port_list=self.sta_list, debug=self.debug)):
            logger.info('All stations are not removed or a timeout occurred. Aborting.')
            exit(1)

    def build(self):
        """Create LANforge port(s) as specified."""
        self.station_profile.use_security(security_type=self.security,
                                          ssid=self.ssid,
                                          passwd=self.password)

        logger.info("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)

        if self.initial_band_pref.upper() not in ["2.4G", "2G", "5G", "6G"]:
            logger.info("Initial band preference should be either 2G or 5G or 6G. Aborting...")
            exit(1)
        else:
            band_pref = int(self.initial_band_pref[0])
            self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
        if not self.eap_method:
            # Not 802.1X, but user may have specified other parameters
            #
            # When add support for other parameters, need to be careful here.
            # Default from args is currently 'None' when unspecified
            if self.key_mgmt:
                # For whatever reason, setting the key mgmt here (using 'set_wifi_extra')
                # clears the 'Key/Phrase' field set by 'add_sta'. Following workaround uses
                # the 'set_wifi_extra' command's 'psk' parameter to set the 'WPA PSK'
                # field in the 'Advanced Configuration' tab
                #
                # Hack to get around unfortunate argparse/initializer default settings which
                # would result in 'null' password when password is not specified
                if not self.password:
                    self.password = "[BLANK]"

                # Have to set 'Advanced/802.1X' flag in order for 'psk' argument to take.
                # This works around limitation in the GUI which does a check for 'Key/Phrase'
                # length when WPA/WPA2/WPA3 enabled (but that field is sadly also cleared here)
                self.station_profile.set_wifi_extra(key_mgmt=self.key_mgmt,
                                                    psk=self.password)
                self.station_profile.set_command_flag(command_name="add_sta",
                                                      param_name="8021x_radius",
                                                      value=1)  # Enable Advanced/802.1X flag
        else:
            # Configure station 802.1X settings
            if self.eap_method == 'TLS':
                self.station_profile.set_wifi_extra(key_mgmt=self.key_mgmt,
                                                    pairwise=self.pairwise_cipher,
                                                    group=self.groupwise_cipher,
                                                    eap=self.eap_method,
                                                    identity=self.eap_identity,
                                                    passwd=self.eap_password,
                                                    private_key=self.private_key,
                                                    ca_cert=self.ca_cert,
                                                    pk_password=self.pk_passwd,
                                                    phase1=self.eap_phase1,
                                                    phase2=self.eap_phase2)
            elif self.eap_method == 'TTLS' or self.eap_method == 'PEAP':
                self.station_profile.set_wifi_extra(key_mgmt=self.key_mgmt,
                                                    pairwise=self.pairwise_cipher,
                                                    group=self.groupwise_cipher,
                                                    eap=self.eap_method,
                                                    identity=self.eap_identity,
                                                    anonymous_identity=self.eap_anonymous_identity,
                                                    passwd=self.eap_password,
                                                    phase1=self.eap_phase1,
                                                    phase2=self.eap_phase2)

            # Security type comes in one of following formats (possibly capitalized),
            # so need to check if substring:
            #   'type'
            #   '<type1|type2>'
            if 'wpa3' in self.security or 'WPA3' in self.security:
                self.station_profile.set_command_param("add_sta", "ieee80211w", 2)

            self.desired_add_sta_flags = []
            self.desired_add_sta_flags_mask = []
            self.station_profile.set_command_flag(command_name="add_sta", param_name="8021x_radius", value=1)  # enable 802.1x flag
            # self.station_profile.set_command_flag(command_name="add_sta", param_name="80211r_pmska_cache", value=1)  # enable 80211r_pmska_cache flag

        # User may want to enable 802.11u, so need to double check (band-aid fix for now).
        # If not specified, then disable it, as the StationProfile class enables it by default,
        # and that may cause headaches.
        #
        # Note that station flags are also set in CreateStation constructor.
        if not self.sta_flags or (self.sta_flags and "80211u_enable" not in self.sta_flags):
            self.station_profile.set_command_flag(command_name="add_sta", param_name="80211u_enable", value=0)

        self.station_profile.set_command_param(
            "set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        if self.set_txo_data is not None:
            self.station_profile.set_wifi_txo(
                txo_ena=self.set_txo_data["txo_enable"],
                tx_power=self.set_txo_data["txpower"],
                pream=self.set_txo_data["pream"],
                mcs=self.set_txo_data["mcs"],
                nss=self.set_txo_data["nss"],
                bw=self.set_txo_data["bw"],
                retries=self.set_txo_data["retries"],
                sgi=self.set_txo_data["sgi"],
            )

        if self.station_profile.create(radio=self.radio,
                                       sta_names_=self.sta_list,
                                       debug=self.debug,
                                       up_=self.up):
            self._pass("Stations created.")
        else:
            self._fail("Stations not properly created.")
        # Custom Wifi setting
        if self.custom_wifi_cmd:
            for sta in self.sta_list:
                self.set_custom_wifi(resource=int(sta.split('.')[1]),
                                     station=str(sta.split('.')[2]),
                                     cmd=self.custom_wifi_cmd)

        if self.up:
            self.station_profile.admin_up()
            if not LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url,
                                                     port_list=self.station_profile.station_names,
                                                     debug_=self.debug,
                                                     timeout=10):
                self._fail("Unable to bring all stations up")
                return
            if self.wait_for_ip(station_list=self.station_profile.station_names, timeout_sec=-1):
                self._pass("All stations got IPs", print_=True)
                self._pass("Station build finished", print_=True)
            else:
                self._fail("Stations failed to get IPs", print_=True)
                self._fail("FAIL: Station build failed", print_=True)
                logger.info("Please re-check the configuration applied")

    def modify_radio(self, mgr, radio, antenna, channel, tx_power, country_code):
        """Configure LANforge WiFi radio port as specified."""
        shelf, resource, radio, *nil = LFUtils.name_to_eid(radio)

        modify_radio = lf_modify_radio.lf_modify_radio(lf_mgr=mgr)
        modify_radio.set_wifi_radio(_resource=resource,
                                    _radio=radio,
                                    _shelf=shelf,
                                    _antenna=antenna,
                                    _channel=channel,
                                    _txpower=tx_power,
                                    _country_code=country_code)

    def get_station_list(self):
        """Query LANforge system for list of all WiFi Station ports."""
        response = super().json_get("/port/list?fields=_links,alias,device,port+type")

        available_stations = []
        for interface_name in response['interfaces']:
            if 'sta' in list(interface_name.keys())[0]:
                available_stations.append(list(interface_name.keys())[0])

        return available_stations


def parse_args():
    """Parse CLI arguments."""
    parser = LFCliBase.create_basic_argparse(  # see create_basic_argparse in ../py-json/LANforge/lfcli_base.py
        prog="create_station.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Create stations",
        description="""\
NAME:       create_station.py

PURPOSE:    Create and configure one or more of WiFi stations ports using the
            specified parent radio.

NOTES:      This script is intended to only create and configure stations. See other scripts
            like 'test_l3.py' to create and run tests.

            By default, the script will also attempt to connect the WiFi stations as configured
            unless the '--create_admin_down' argument is specified.

            --mode <mode_num>
                Set the station WiFi mode (e.g. to configure a 802.11be radio as 802.11ax)
                See the 'add_sta' command's mode option in the CLI documentation for
                available mode settings. Link here: http://www.candelatech.com/lfcli_ug.php#add_sta

            --station_flags  <station_flags>
                Comma-separated list of flags to configure the station with (e.g. 'ht160_enable,disable_sgi'
                to enable 160MHz channel usage and disable 802.11ac short guard interval (SGI), respectively).
                Note that other options like '--security' configure authentication-based station flags.
                See the 'add_sta' command's 'flags' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#add_sta

            --country_code 840
                United States   :   840     |       Dominican Rep   :   214     |      Japan (JE2)     :   397     |      Portugal        :   620
                Albania         :   8       |       Ecuador         :   218     |      Jordan          :   400     |      Pueto Rico      :   630
                Algeria         :   12      |       Egypt           :   818     |      Kazakhstan      :   398     |      Qatar           :   634
                Argentina       :   32      |       El Salvador     :   222     |      North Korea     :   408     |      Romania         :   642
                Bangladesh      :   50      |       Estonia         :   233     |      South Korea     :   410     |      Russia          :   643
                Armenia         :   51      |       Finland         :   246     |      South Korea     :   411     |      Saudi Arabia    :   682
                Australia       :   36      |       France          :   250     |      Kuwait          :   414     |      Singapore       :   702
                Austria         :   40      |       Georgia         :   268     |      Latvia          :   428     |      Slovak Republic :   703
                Azerbaijan      :   31      |       Germany         :   276     |      Lebanon         :   422     |      Slovenia        :   705
                Bahrain         :   48      |       Greece          :   300     |      Liechtenstein   :   438     |      South Africa    :   710
                Barbados        :   52      |       Guatemala       :   320     |      Lithuania       :   440     |      Spain           :   724
                Belarus         :   112     |       Haiti           :   332     |      Luxembourg      :   442     |      Sweden          :   752
                Belgium         :   56      |       Honduras        :   340     |      Macau           :   446     |      Switzerland     :   756
                Belize          :   84      |       Hong Kong       :   344     |      Macedonia       :   807     |      Syria           :   760
                Bolivia         :   68      |       Hungary         :   348     |      Malaysia        :   458     |      Taiwan          :   158
                BiH             :   70      |       Iceland         :   352     |      Mexico          :   484     |      Thailand        :   764
                Brazil          :   76      |       India           :   356     |      Monaco          :   492     |      Trinidad &Tobago:   780
                Brunei          :   96      |       Indonesia       :   360     |      Morocco         :   504     |      Tunisia         :   788
                Bulgaria        :   100     |       Iran            :   364     |      Netherlands     :   528     |      Turkey          :   792
                Canada          :   124     |       Ireland         :   372     |      Aruba           :   533     |      U.A.E.          :   784
                Chile           :   152     |       Israel          :   376     |      New Zealand     :   554     |      Ukraine         :   804
                China           :   156     |       Italy           :   380     |      Norway          :   578     |      United Kingdom  :   826
                Colombia        :   170     |       Jamaica         :   388     |      Oman            :   512     |      Uruguay         :   858
                Costa Rica      :   188     |       Japan           :   392     |      Pakistan        :   586     |      Uzbekistan      :   860
                Croatia         :   191     |       Japan (JP1)     :   393     |      Panama          :   591     |      Venezuela       :   862
                Cyprus          :   196     |       Japan (JP0)     :   394     |      Peru            :   604     |      Vietnam         :   704
                Czech Rep       :   203     |       Japan (JP1-1)   :   395     |      Philippines     :   608     |      Yemen           :   887
                Denmark         :   208     |       Japan (JE1)     :   396     |      Poland          :   616     |      Zimbabwe        :   716

            --no_pre_cleanup
                Disables station cleanup before creation of stations. Default behavior will remove any existing stations.

            --cleanup
                Add this flag to clean up stations after creation

            --initial_band_pref
                Add this argument to set initial band preference to be either 2G or 5G or 6G.

            --eap_method <eap_method>
                EAP method used by station in authentication.
                See the 'set_wifi_extra' command's 'eap' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#set_wifi_extra

            --key_mgmt <protocol>
                Key management protocol used by the station in authentication.

            --pairwise_cipher <cipher>
                Pairwise cipher used by station in authentication.
                See the 'set_wifi_extra' command's 'pairwise' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#set_wifi_extra

            --groupwise_cipher <cipher>
                Groupwise cipher used by station in authentication.
                See the 'set_wifi_extra' command's 'groupwise' option in the CLI documentation for available options.
                Link here: http://www.candelatech.com/lfcli_ug.php#set_wifi_extra

            --eap_identity <eap_identity>
                EAP identity (i.e. username) used by the station in authentication.

            --eap_password <eap_password>
                EAP password used by the station in authentication.

            --pk_passwd <password>
                Private key password used by the station in authentication. Required for TLS-based authentication.

            --ca_cert <path_to_certificate>
                Path to Certificate authority certificate used by the station in authentication.
                Required for TLS-based authentication.
                Note this is the path on the LANforge system where this station will be created.

            --private_key <path_to_private_key>
                Path to private key used by the station in authentication. Required for TLS-based authentication.
                Note this is the path on the LANforge system where this station will be created.

EXAMPLE:
            # Create a single station
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --passwd    <password> \
                   --security  wpa2

            # Create multiple stations with initial band preference 5G
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --passwd    <password> \
                   --security  wpa2 \
                   --num_stations 10 \
                   --initial_band_pref 5G

            # Create multiple stations
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --num_stations  10

            # Create a multiple stations, all associated to specific BSSID
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --bssid     <bssid> \
                   --passwd    <password> \
                   --security  wpa2

            # Create a multiple stations with specific numbering scheme
            # In this example, create five stations with names of the format: "sta1000", "sta1001", "sta1002", etc.
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --start_id      1000 \
                   --num_stations  5

            # Create a station, configuring radio settings like antenna, channel, etc.
            # In this example, configure radio to use antennas (2x2 station) and channel 6
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --radio_antenna 2 \
                   --radio_channel 6

            # Create a station, configuring the station to be a specific WiFi mode
            # (e.g. configuring an 802.11ax-capable radio to create an 802.11ac station)
            # See the 'add_sta' command's mode option in the CLI documentation for
            # available mode settings. Link here: http://www.candelatech.com/lfcli_ug.php#add_sta
               ./create_station.py \
                   --mgr       <lanforge ip> \
                   --radio     1.1.wiphy1 \
                   --ssid      <ssid> \
                   --passwd    <password> \
                   --security  wpa2 \
                   --mode      6

            # Create a station, configuring specific station flags
            # In this example, enable 160MHz channels and disable 802.11ac short guard interval (SGI).
               ./create_station.py \
                   --mgr           <lanforge ip> \
                   --radio         1.1.wiphy1 \
                   --ssid          <ssid> \
                   --passwd        <password> \
                   --security      wpa2 \
                   --radio_antenna 2 \
                   --radio_channel 6 \
                   --station_flags "ht160_enable,disable_sgi"

            # Create a station using TLS-based enterprise authentication
            # Note that paths are paths on the LANforge system where the station will be created.
               ./create_station.py \
                   --mgr               <lanforge ip> \
                   --radio             1.1.wiphy1 \
                   --ssid              <ssid> \
                   --security          <wpa2|wpa3> \
                   --key_mgmt          <key_mgmt> \
                   --pairwise_cipher   <cipher> \
                   --groupwise_cipher  <cipher> \
                   --eap_method        TLS \
                   --eap_identity      <username> \
                   --eap_password      <password> \
                   --pk_passwd         <password> \
                   --private_key       <path> \
                   --ca_cert           <path>

            # Create a station using TTLS-based enterprise authentication
               ./create_station.py \
                   --mgr               <lanforge ip> \
                   --radio             1.1.wiphy1 \
                   --ssid              <ssid> \
                   --security          <wpa2|wpa3> \
                   --key_mgmt          <TTLS|PEAP> \
                   --pairwise_cipher   <cipher> \
                   --groupwise_cipher  <cipher> \
                   --eap_method        TTLS \
                   --eap_identity      <username> \
                   --eap_password      <password>

            #    Create station specifying a custom 'wpa_supplicant' config command
            #    In this example, specify a background scanning 'wpa_supplicant' command, useful for roaming.
            #    Here, the background scan is configured to a threshold of -65 dBm RSSI with a short and long interval of 50 and 300 seconds.
            #    See 'man wpa_supplicant.conf' for more information.
                ./create_station.py \
                    --mgr               <lanforge ip> \
                    --radio             1.1.wiphy1 \
                    --ssid              <ssid> \
                    --passwd            <password> \
                    --security          wpa2 \
                    --custom_wifi_cmd   'bgscan="simple:50:-65:300"'

SCRIPT_CLASSIFICATION:
            Creation

SCRIPT_CATEGORIES:
            Functional

STATUS:     Functional

VERIFIED_ON:
            9-JUN-2023,
            GUI Version:  5.4.6
            Kernel Version: 5.19.17+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README:
            False
""")
    required = parser.add_argument_group('required arguments')
    required.add_argument('--start_id',
                          type=int,
                          help='Specify the station starting id \n e.g: --start_id <value> default 0',
                          default=0)

    optional = parser.add_argument_group('Optional arguments')
    optional.add_argument("--prefix",
                          type=str,
                          help="Station prefix. Default: \'sta\'",
                          default="sta")
    optional.add_argument("--create_admin_down",
                          help='Create ports in admin down state.',
                          action='store_true')
    optional.add_argument("--bssid",
                          type=str,
                          help="AP BSSID. For example, \"00:00:00:00:00:00\".",
                          default="DEFAULT")  # TODO: Fix 'null' when not set issue (REST server-side issue)
    optional.add_argument('--mode',
                          help='Mode for your station (as a number)',
                          default=0)
    optional.add_argument('--station_flags',
                          '--station_flag',
                          dest='station_flags',
                          help='station flags to add. eg: --station_flags ht40_disable',
                          required=False,
                          default=None)
    optional.add_argument("--mac_pattern",
                          help="MAC randomization pattern for created stations. "
                               "In full MAC address pattern, the \'*\' indicates "
                               "randomizable characters. Most users will not adjust "
                               "this option. Note that this does not explicitly set "
                               "the locally-administered address bit.",
                          default="xx:xx:xx:*:*:xx")
    optional.add_argument("--radio_antenna",
                          help='Number of spatial streams: \n'
                          ' default = -1 \n'
                          ' 0 Diversity (All) \n'
                          ' 1 Fixed-A (1x1) \n'
                          ' 4 AB (2x2) \n'
                          ' 7 ABC (3x3) \n'
                          ' 8 ABCD (4x4) \n'
                          ' 9 (8x8) \n',
                          default='0')
    optional.add_argument("--radio_channel",
                          help='Radio Channel: \n'
                          ' default: AUTO \n'
                          ' e.g:   --radio_channel 6 (2.4G) \n'
                          '\t--radio_channel 36 (5G) \n',
                          default='AUTO')
    optional.add_argument("--radio_tx_power",
                          help='Radio tx-power \n'
                          ' default: AUTO system defaults',
                          default='AUTO')
    optional.add_argument("--country_code",
                          help='Radio Country Code:\n'
                               'e.g: \t--country_code 840')
    optional.add_argument("--eap_method",
                          type=str,
                          help='Enter EAP method e.g: TLS')
    optional.add_argument("--eap_identity",
                          "--radius_identity",
                          dest="eap_identity",
                          type=str,
                          help="This is synonymous with the RADIUS username.")
    optional.add_argument("--eap_anonymous_identity",
                          type=str,
                          help="",
                          default="[BLANK]")  # TODO: Fix root cause of 'null' when not set issue (REST server-side issue)
    optional.add_argument("--eap_password",
                          "--radius_passwd",
                          dest="eap_password",
                          type=str,
                          help="This is synonymous with the RADIUS user's password.")
    optional.add_argument("--eap_phase1",
                          type=str,
                          help="EAP Phase 1 (outer authentication, i.e. TLS tunnel) parameters.\n"
                               "For example, \"peapver=0\" or \"peapver=1 peaplabel=1\".\n"
                               "Some WPA Enterprise setups may require \"auth=MSCHAPV2\"",
                          default="[BLANK]")  # TODO: Fix root cause of 'null' when not set issue (REST server-side issue)
    optional.add_argument("--eap_phase2",
                          type=str,
                          help="EAP Phase 2 (inner authentication) parameters.\n"
                               "For example, \"autheap=MSCHAPV2 autheap=MD5\" for EAP-TTLS.",
                          default="[BLANK]")  # TODO: Fix root cause of 'null' when not set issue (REST server-side issue)
    optional.add_argument("--pk_passwd",
                          type=str,
                          help='Enter the private key password')
    optional.add_argument("--ca_cert",
                          type=str,
                          help='Enter path for certificate e.g: /home/lanforge/ca.pem')
    optional.add_argument("--private_key",
                          type=str,
                          help='Enter private key path e.g: /home/lanforge/client.p12')
    optional.add_argument("--key_mgmt",
                          type=str,
                          help="Authentication key management. Combinations are supported.\n")
    optional.add_argument("--pairwise_cipher",
                          help='Pairwise Ciphers\n'
                               'DEFAULT\n'
                               'CCMP\n'
                               'TKIP\n'
                               'NONE\n'
                               'CCMP-TKIP\n'
                               'CCMP-256\n'
                               'GCMP\n'
                               'GCMP-256\n'
                               'CCMP/GCMP-256',
                               default='[BLANK]')
    optional.add_argument("--groupwise_cipher",
                          help='Groupwise Ciphers\n'
                               'DEFAULT\n'
                               'CCMP\n'
                               'TKIP\n'
                               'WEP104\n'
                               'WEP40\n'
                               'GTK_NOT_USED\n'
                               'GCMP-256\n'
                               'CCMP-256\n'
                               'GCMP/CCMP-256\n'
                               'ALL',
                          default='[BLANK]')
    optional.add_argument("--no_pre_cleanup",
                          help='Add this flag to stop cleaning up before station creation',
                          action='store_true')
    optional.add_argument("--cleanup",
                          help='Add this flag to clean up stations after creation',
                          action='store_true')
    optional.add_argument("--custom_wifi_cmd",
                          help="Mention the custom wifi command.")
    optional.add_argument("--initial_band_pref",
                          type=str,
                          default="0",
                          help="Specify the initial band preference for created stations: '2G' for 2.4GHz,\n"
                          "'5G' for 5GHz, or '6G' for 6GHz.")

    return parser.parse_args()


def validate_args(args):
    """Validate CLI arguments."""
    if args.radio is None:
        logger.error("--radio required")
        exit(1)

    # TODO: Revisit these requirements. May have made some incorrect assumptions
    if args.eap_method is not None:
        if args.eap_identity is None:
            logger.error("--eap_identity required")
            exit(1)
        elif args.eap_password is None:
            logger.error("--eap_password required")
            exit(1)
        elif args.key_mgmt is None:
            logger.error("--key_mgmt required")
            exit(1)
        elif args.eap_method == 'TLS':
            if args.pk_passwd is None:
                logger.error("--pk_passwd required")
                exit(1)
            elif args.ca_cert is None:
                logger.error('--ca_cert required')
                exit(1)
            elif args.private_key is None:
                logger.error('--private_key required')
                exit(0)

        # Only need to check WPA3 ciphers because user requests 802.1X authentication.
        # Personal WPA3 always uses SAE, so default '[BLANK]' is fine if ciphers
        # aren't specified.
        #
        # Security type comes in one of following formats (possibly capitalized),
        # so need to check if substring:
        #   'type'
        #   '<type1|type2>'
        if 'wpa3' in args.security or 'WPA3' in args.security:
            if args.pairwise_cipher == '[BLANK]':
                logger.error('--pairwise_cipher required')
                exit(1)
            elif args.groupwise_cipher == '[BLANK]':
                logger.error('--groupwise_cipher required')
                exit(1)


def main():
    """Create LANforge WiFi station port(s) using specified options."""
    args = parse_args()

    help_summary = "This script will create and configure one or more WiFi station ports " \
                   "using the single specified WiFi radio parent port."

    if args.help_summary:
        print(help_summary)
        exit(0)

    validate_args(args)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    num_sta = 1
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_stations_converted = int(args.num_stations)
        num_sta = num_stations_converted

    station_list = LFUtils.port_name_series(prefix=args.prefix,
                                            start_id=args.start_id,
                                            end_id=args.start_id + num_sta - 1,
                                            padding_number=10000,
                                            radio=args.radio)

    logger.info("Stations to create: {}".format(station_list))
    create_station = CreateStation(**vars(args),
                                   sta_list=station_list,
                                   up=(not args.create_admin_down),
                                   password=args.passwd,
                                   set_txo_data=None)

    if not args.no_pre_cleanup:
        create_station.cleanup()
    else:
        already_available_stations = create_station.get_station_list()
        if len(already_available_stations) > 0:
            used_indices = [int(station_id.split('sta')[1]) for station_id in already_available_stations]
            for new_station in station_list:
                if new_station in already_available_stations:
                    logger.error('Some stations are already existing in the LANforge from the given start id.')
                    logger.error('You can create stations from the start id {}'.format(max(used_indices) + 1))
                    exit(1)

    create_station.modify_radio(mgr=args.mgr,
                                radio=args.radio,
                                antenna=args.radio_antenna,
                                channel=args.radio_channel,
                                tx_power=args.radio_tx_power,
                                country_code=args.country_code)
    create_station.build()

    if args.cleanup:
        create_station.cleanup()

    if create_station.passes():
        logger.info('Created %s stations' % num_sta)
        create_station.exit_success()
    else:
        create_station.exit_fail()


if __name__ == "__main__":
    main()
