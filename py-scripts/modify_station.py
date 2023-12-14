#!/usr/bin/env python3
"""
    Script for modifying stations.
"""
import sys
import os
import importlib
import argparse
import pprint

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
set_port = importlib.import_module("py-json.LANforge.set_port")
add_sta = importlib.import_module("py-json.LANforge.add_sta")
import lf_modify_radio


class ModifyStation(Realm):
    ANTENNA_VALUES: dict = {
        "All": 0, "1x1": 1, "2x2": 4, "3x3": 7, "4x4": 8, "8x8": 9
    }

    def __init__(self,
                 _ssid="NA",
                 _state=None,
                 _bssid=None,
                 _security="NA",
                 _password="NA",
                 _mac="NA",
                 _host=None,
                 _port=None,
                 _station_list=None,
                 _enable_flags=None,
                 _disable_flags=None,
                 _number_template="00000",
                 _radio=None,
                 _ip=None,
                 _mode=None,
                 _netmask=None,
                 _gateway=None,
                 _channel=None,
                 _txpower=None,
                 _antennas=None,
                 _country=None,
                 _proxy_str=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _dhcp=True):
        super().__init__(_host,
                         _port)
        self.host = _host
        self.port = _port
        self.ssid = _ssid
        self.state = _state
        self.bssid = _bssid
        self.security = _security
        self.password = _password
        self.mac = _mac
        self.station_list = _station_list
        self.enable_flags = _enable_flags
        self.disable_flags = _disable_flags
        self.radio = _radio
        self.timeout = 120
        self.number_template = _number_template
        self.debug = _debug_on
        self.dhcp = _dhcp
        self.mode = _mode

        self.station_profile = self.new_station_profile()
        self.station_profile.station_names = self.station_list
        self.station_profile.up = self.state
        self.station_profile.ssid = self.ssid
        self.station_profile.bssid = self.bssid
        self.station_profile.security = self.security
        self.station_profile.ssid_pass = self.password
        self.station_profile.mac = self.mac
        self.station_profile.dhcp = self.dhcp
        self.station_profile.debug = self.debug
        self.station_profile.desired_add_sta_flags = self.enable_flags
        if self.enable_flags or self.disable_flags:
            self.station_profile.desired_add_sta_flags_mask = self.enable_flags + self.disable_flags
        self.station_profile.mode = _mode
        self.station_profile.ip = _ip
        self.station_profile.netmask = _netmask
        self.station_profile.gateway = _gateway

        self.ip = _ip
        self.netmask = _netmask
        self.gateway = _gateway
        self.channel = _channel
        self.txpower = _txpower
        self.antennas = _antennas
        self.country = _country

    def list_ports(self):
        response = super().json_get("/port/list?fields=port,alias,down")
        if not response:
            raise ValueError("Unable to make request")

        if "interfaces" not in response:
            pprint.pprint(["Full response:", response])
            return
        for record in response["interfaces"]:
            # pprint.pprint(["record", record])
            eid = list(record.keys())[0]
            print(f"{eid}")

    def list_stations(self):
        response = super().json_get("/port/list?fields=port,alias,down,port+type")
        if not response:
            raise ValueError("Unable to make request")

        if "interfaces" not in response:
            pprint.pprint(["Full response:", response])
            return

        for record in response["interfaces"]:
            # pprint.pprint(["record", record])
            eid = list(record.keys())[0]
            if record[eid]["port type"] == "WIFI-STA":
                print(f"{eid}")

    def set_station(self):
        print(f"modifying station on radio {self.radio}")
        result = self.station_profile.modify(radio=self.radio)
        return result

    def adjust_radio(self, radio_eid=None):
        if not radio_eid:
            raise ValueError("adjust_radio: requires radio eid")

        radio_adjuster = lf_modify_radio.lf_modify_radio(lf_mgr=self.host,
                                                         lf_port=self.port,
                                                         lf_user=None,
                                                         lf_passwd=None,
                                                         debug=self.debug,
                                                         static_ip=None,
                                                         ip_mask=None,
                                                         gateway_ip=None)

        eid_hunks: list = radio_eid.split(".")
        if len(eid_hunks) < 3:
            raise ValueError(f"adjust_radio: wants a three-part eid (eg: 1.2.wiphy0), but has [{radio_eid}]")

        if self.channel or self.txpower or self.antennas or self.country:
            print("checking to see if provided radio matches provided station")
            port_list = self.find_ports_like(pattern=self.station_list[0],
                                             _fields="port,alias,parent dev,port type",
                                             debug_=True)
            if not port_list:
                raise ValueError(f"station:{self.station_list[0]} does not correspond to radio: {self.radio}")
            num_matching=0
            pprint.pprint(["port_list:", port_list])
            if isinstance(port_list, dict):
                for eid, record in port_list.items():
                    if not record["parent dev"]:
                        continue
                    if self.radio.endswith(record["parent dev"]):
                        num_matching+=1
            elif isinstance(port_list, list):
                for record in port_list:
                    if not record["parent dev"]:
                        continue
                    if record["parent dev"] == self.radio:
                        num_matching+=1
            if num_matching < 1:
                raise ValueError(f"Station [{self.station_list[0]}] and Radio[{self.radio}] do not correspond")

        if self.channel:
            print("would set radio channel")

        if self.txpower:
            print("would set radio txpower")

        if self.antennas:
            print("would set radio nss")

        print(f"...done {self.radio}")
        pprint.pprint(["EID HUNKS", eid_hunks, "ONE:", eid_hunks[1]])
        res: int = eid_hunks[1]
        radio: str = str(eid_hunks[2])

        radio_adjuster.set_wifi_radio(_resource=res,
                                      _radio=radio,
                                      _shelf=1,
                                      _antenna=self.antennas,
                                      _channel=self.channel,
                                      _txpower=self.txpower,
                                      _country_code=self.country)

    @staticmethod
    def convert_antenna(antenna_str=None):
        if not antenna_str:
            return 0
        if antenna_str in ModifyStation.ANTENNA_VALUES:
            return ModifyStation.ANTENNA_VALUES[antenna_str]
        return 0


def main():
    parser = LFCliBase.create_basic_argparse(
        prog='modify_station.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Modify stations on a system. Use the enable_flag to create a flag on a station. Turn off a flag with \
         the disable_flag option. A list of available flags are available in the add_station.py file in \
         py-json/LANforge.
            ''',

        description='''\
        modify_station.py
        --------------------
        Command example:
        ./modify_station.py --mgr localhost --list_ports
        
        ./modify_station.py --mgr localhost --list_stations
        
        ./modify_station.py
            --radio         wiphy0
            --station       1.1.sta0000
            --set_state     up|down
            --security      open
            --ssid          netgear
            --passwd        BLANK
            --enable_flag   osen_enable
            --disable_flag  ht160_enable
            --bssid         00:11:22:33:44:55
            --mode          abgnAX
            --rate          [mcs rate available from txo-feautres]
            --ip            192.168.45.2
            --netmask       255.255.255.0
            --gateway       192.168.45.1
            --channel       6
            --txpower       24
            --antennas      2x2
            --country       [soon] US
            --debug
        --------------------
        Station flags are currently defined as:
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
        80211r_pmska_cache   | 0x4000000    # Enable opportunistic PMSKA caching for WPA2 (Related to 802.11r).
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
''')

    # the default value of passwd in parent parser is '[BLANK]' and that's destructive here
    parser.set_defaults(passwd='NA')

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--enable_flag',
                          default=list(),
                          action='append',
                          help='station flags to add')
    optional.add_argument('--disable_flag',
                          help='station flags to disable',
                          default=list(),
                          action='append')
    optional.add_argument('--station',
                          help='station to modify',
                          # required=True, # making this required breaks --help_summary
                          action='append')
    optional.add_argument('--set_state', '--state', '--up',
                          choices=['DOWN', 'UP', 'down', 'up'],
                          help="admin port UP or DOWN")
    optional.add_argument('--mac',
                          default="NA",
                          help="MAC address of the station")
    optional.add_argument('--mode',
                          default='NA',
                          help=f"set station wifi mode: "
                               f"{', '.join(list(add_sta.add_sta_modes.keys()))}")
    optional.add_argument('--bssid',
                          help="specify the BSSID of the AP to associate with, or DEFAULT")
    optional.add_argument('--ip',
                          help="specify IP to apply to port (ipv4 1.2.3.4 or DHCP)")
    optional.add_argument('--netmask',
                          help="specify netmask to apply to port")
    optional.add_argument('--gateway',
                          help="specify gateway to apply to port")
    optional.add_argument('--channel',
                          help="specify channel for radio, requires --radio")
    optional.add_argument('--txpower',
                          help="specify txpower for radio, requires --radio, use 0-25 or DEFAULT or -1")

    optional.add_argument('--antennas', '--antenna',
                          choices=["All", "1x1", "2x2", "3x3", "4x4", "8x8"],
                          help="specify antenna diversity for radio (NSS), requires --radio")
    optional.add_argument('--country',
                          help="sets country region for all radios in a resource; requires --radio,"
                               " all radios on that resource will be changed")
    optional.add_argument('--list_stations',
                          action="store_true",
                          help="lists station by Eid")
    optional.add_argument('--list_ports',
                          action="store_true",
                          help="lists ports by Eid")
    args = parser.parse_args()

    if args.help_summary:
        print("Modify stations on a system. Use the enable_flag to create a flag on a station. Turn off a flag with "
              "the disable_flag option. A list of available flags are available in the add_station.py file in "
              "py-json/LANforge.")
        exit(0)
    if args.list_stations:
        modify_station = ModifyStation(_host=args.mgr,
                                       _port=args.mgr_port,
                                       _debug_on=args.debug)
        modify_station.list_stations()
        exit(0)
    if args.list_ports:
        modify_station = ModifyStation(_host=args.mgr,
                                       _port=args.mgr_port,
                                       _debug_on=args.debug)
        modify_station.list_ports()
        exit(0)

    if args.mode != "NA":
        if args.mode not in add_sta.add_sta_modes:
            raise ValueError("wifi mode not found, expecting one of: "
                             f"{', '.join(list(add_sta.add_sta_modes.keys()))}")
    if not args.radio:
        print("--radio eid required, eg 1.6.wiphy0")
        exit(1)

    if (not args.enable_flag) or (not args.disable_flag):
        print("No --enable_flag or --disable_flags listed to change.")

    if (not args.station) or (len(args.station) < 1):
        raise ValueError("requires --station eid (eg: 1.1.wlan0)")

    modify_station = ModifyStation(_host=args.mgr,
                                   _port=args.mgr_port,
                                   _state=args.set_state,
                                   _ssid=args.ssid,
                                   _bssid=args.bssid,
                                   _password=args.passwd,
                                   _security=args.security,
                                   _mac=args.mac,
                                   _station_list=args.station,
                                   _radio=args.radio,
                                   _proxy_str=args.proxy,
                                   _enable_flags=args.enable_flag,
                                   _disable_flags=args.disable_flag,
                                   _ip=args.ip,
                                   _mode=args.mode,
                                   _netmask=args.netmask,
                                   _gateway=args.gateway,
                                   _channel=args.channel,
                                   _txpower=args.txpower,
                                   _antennas=ModifyStation.ANTENNA_VALUES[args.antennas],
                                   _country=args.country,
                                   _debug_on=args.debug)
    modifications: int = 0
    if args.ip == "DHCP" or args.ip == "dhcp":
        modify_station.dhcp = True
    if args.set_state or args.ssid or args.bssid or args.passwd \
            or args.mac or args.enable_flag or args.disable_flag \
            or args.ip or args.netmask or args.gateway:
        modifications += 1
        modify_station.set_station()

    if args.channel or args.txpower or args.antennas or args.country:
        modifications += 1
        modify_station.adjust_radio(radio_eid=args.radio)

    if modifications < 1:
        print("** ** No stations modified ** **")


if __name__ == "__main__":
    main()
