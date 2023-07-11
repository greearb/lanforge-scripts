#!/usr/bin/env python3
"""
NAME: create_station.py

PURPOSE: create_station.py will create a variable number of stations, and connect them to a specified wireless network.

EXAMPLE:
         # For creating the single stations

            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> --security wpa2

         # For creating the multiple stations
         
            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 22 --num_stations 10 --ssid <ssid> --passwd <password> --security wpa2

         # For creating the stations with radio settings like anteena, channel, etc.
         
            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> --security wpa2
            --radio_antenna 4 --radio_channel 6

         # For station enabled with additional flags
            
            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> --security wpa2
            --station_flag <staion_flags>
           

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional 

NOTES: 
        Does not create cross connects 
        Mainly used to determine how to create a station
         
        * We can also specify the mode for the stations using "--mode" argument
    
            --mode   1
                {"auto"   : "0",
                "a"      : "1",
                "b"      : "2",
                "g"      : "3",
                "abg"    : "4",
                "abgn"   : "5",
                "bgn"    : "6",
                "bg"     : "7",
                "abgnAC" : "8",
                "anAC"   : "9",
                "an"     : "10",
                "bgnAC"  : "11",
                "abgnAX" : "12",
                "bgnAX"  : "13"}

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --mode 6

            --station_flag  <staion_flags>
                add_sta_flags = {
                "osen_enable"          :  Enable OSEN protocol (OSU Server-only Authentication)
                "ht40_disable"         :  Disable HT-40 even if hardware and AP support it.
                "ht160_enable"         :  Enable HT160 mode.
                "disable_sgi"          :  Disable SGI (Short Gu
                "hs20_enable"          :  Enable Hotspot 2.0 (HS20) feature.  R
                "txo-enable"           :  Enable/disable tx-offloads, typically managed by set_wifi_txo command
                "custom_conf"          :  Use Custom wpa_supplicant config file.
                "ibss_mode"            :  Station should be in IBSS mode.
                "mesh_mode"            :  Station should be in MESH mode.
                "wds-mode"             :  WDS station (sort of like a lame mesh), not supported on ath10k
                "scan_ssid"            :  Enable SCAN-SSID flag in wpa_supplicant.
                "passive_scan"         :  Use passive scanning (don't send probe requests).
                "lf_sta_migrate"       :  OK-To-Migrate (Allow station migration between LANforge radios)
                "disable_fast_reauth"  :  Disable fast_reauth option for virtual stations.
                "power_save_enable"    :  Station should enable power-save.  May not work in all drivers/configurations.
                "disable_roam"         :  Disable automatic station roaming based on scan results.
                "no-supp-op-class-ie"  :  Do not include supported-oper-class-IE in assoc requests.  May work around AP bugs.
                "use-bss-transition"   :  Enable BSS transition.
                "ft-roam-over-ds"      :  Roam over DS when AP supports it.
                "disable_ht80"         :  Disable HT80 (for AC chipset NICs only)}

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --station_flag power_save_enable

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
                    Disables station cleanup before creation of stations

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --no_pre_cleanup


            --cleanup
                    Disables station cleanup after creation of stations

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --cleanup

STATUS: BETA RELEASE

VERIFIED_ON:   9-JUN-2023,
             GUI Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

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


class CreateStation(Realm):
    def __init__(self,
                 _ssid=None,
                 _security=None,
                 _password=None,
                 _host=None,
                 _port=None,
                 _mode=0,
                 _sta_list=None,
                 _sta_flags=None,
                 _number_template="00000",
                 _radio="wiphy0",
                 _proxy_str=None,
                 _debug_on=False,
                 _up=True,
                 _set_txo_data=None,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(_host,
                         _port)
        self.host = _host
        self.port = _port
        self.ssid = _ssid
        self.security = _security
        self.password = _password
        self.mode = _mode
        self.sta_list = _sta_list
        self.sta_flags = _sta_flags
        self.radio = _radio
        self.timeout = 120
        self.number_template = _number_template
        self.debug = _debug_on
        self.up = _up
        self.set_txo_data = _set_txo_data
        self.station_profile = self.new_station_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = self.mode
        # if self.sta_flags is not None:
        #     self.station_profile.desired_add_sta_flags = self.sta_flags
        #     self.station_profile.desired_add_sta_mask = self.sta_flags

        if self.sta_flags is not None:
            _flags = self.sta_flags.split(',')
            for flags in _flags:
                print(flags)
                self.station_profile.set_command_flag("add_sta", flags, 1)

        if self.debug:
            print("----- Station List ----- ----- ----- ----- ----- ----- \n")
            pprint.pprint(self.sta_list)
            print("---- ~Station List ----- ----- ----- ----- ----- ----- \n")

    def cleanup(self):
        for station in self.sta_list:
            print('Removing the station {} if exists'.format(station))
            self.rm_port(station, check_exists=True)
        if (not LFUtils.wait_until_ports_disappear(base_url=self.station_profile.lfclient_url, port_list=self.sta_list, debug=self.debug)):
            print('All stations are not removed or a timeout occurred.')
            print('Aborting the test.')
            exit(1)

    def build(self):
        # Build stations
        self.station_profile.use_security(
            self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)

        print("Creating stations")
        self.station_profile.set_command_flag(
            "add_sta", "create_admin_down", 1)
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

        if self.station_profile.create(
            radio=self.radio,
            sta_names_=self.sta_list,
            debug=self.debug):
            self._pass("Stations created.")
        else:
            self._fail("Stations not properly created.")

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
        shelf, resource, radio, *nil = LFUtils.name_to_eid(radio)

        modify_radio = lf_modify_radio.lf_modify_radio(lf_mgr=mgr)
        modify_radio.set_wifi_radio(_resource=resource, _radio=radio, _shelf=shelf, _antenna=antenna, _channel=channel,
                                    _txpower=tx_power,_country_code=country_code)
        
    def get_station_list(self):
        response = super().json_get("/port/list?fields=_links,alias,device,port+type")
        available_stations = []
        for interface_name in response['interfaces']:
            # print('sta' in list(interface_name.keys())[0])
            if('sta' in list(interface_name.keys())[0]):
                available_stations.append(list(interface_name.keys())[0])
        return(available_stations)
        

def main():
    parser = LFCliBase.create_basic_argparse(  # see create_basic_argparse in ../py-json/LANforge/lfcli_base.py
        prog='create_station.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Create stations
            ''',

        description='''\

NAME: create_station.py

PURPOSE: create_station.py will create a variable number of stations, and connect them to a specified wireless network.

EXAMPLE:
         # For creating the single stations

            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> --security wpa2

         # For creating the multiple stations
         
            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 22 --num_stations 10 --ssid <ssid> --passwd <password> --security wpa2

         # For creating the stations with radio settings like anteena, channel, etc.
         
            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> --security wpa2
            --radio_antenna 4 --radio_channel 6

         # For station enabled with additional flags
            
            create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> --security wpa2
            --station_flag <staion_flags>
           

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional 

NOTES: 
        Does not create cross connects 
        Mainly used to determine how to create a station
         
        * We can also specify the mode for the stations using "--mode" argument
    
            --mode   1
                {"auto"   : "0",
                "a"      : "1",
                "b"      : "2",
                "g"      : "3",
                "abg"    : "4",
                "abgn"   : "5",
                "bgn"    : "6",
                "bg"     : "7",
                "abgnAC" : "8",
                "anAC"   : "9",
                "an"     : "10",
                "bgnAC"  : "11",
                "abgnAX" : "12",
                "bgnAX"  : "13"}

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --mode 6

            --station_flag  <staion_flags>
                add_sta_flags = {
                "osen_enable"          :  Enable OSEN protocol (OSU Server-only Authentication)
                "ht40_disable"         :  Disable HT-40 even if hardware and AP support it.
                "ht160_enable"         :  Enable HT160 mode.
                "disable_sgi"          :  Disable SGI (Short Gu
                "hs20_enable"          :  Enable Hotspot 2.0 (HS20) feature.  R
                "txo-enable"           :  Enable/disable tx-offloads, typically managed by set_wifi_txo command
                "custom_conf"          :  Use Custom wpa_supplicant config file.
                "ibss_mode"            :  Station should be in IBSS mode.
                "mesh_mode"            :  Station should be in MESH mode.
                "wds-mode"             :  WDS station (sort of like a lame mesh), not supported on ath10k
                "scan_ssid"            :  Enable SCAN-SSID flag in wpa_supplicant.
                "passive_scan"         :  Use passive scanning (don't send probe requests).
                "lf_sta_migrate"       :  OK-To-Migrate (Allow station migration between LANforge radios)
                "disable_fast_reauth"  :  Disable fast_reauth option for virtual stations.
                "power_save_enable"    :  Station should enable power-save.  May not work in all drivers/configurations.
                "disable_roam"         :  Disable automatic station roaming based on scan results.
                "no-supp-op-class-ie"  :  Do not include supported-oper-class-IE in assoc requests.  May work around AP bugs.
                "use-bss-transition"   :  Enable BSS transition.
                "ft-roam-over-ds"      :  Roam over DS when AP supports it.
                "disable_ht80"         :  Disable HT80 (for AC chipset NICs only)}

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --station_flag power_save_enable

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
                    Disables station cleanup before creation of stations

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --no_pre_cleanup


            --cleanup
                    Disables station cleanup after creation of stations

            example:
                    create_station.py --mgr <lanforge ip> --radio wiphy1 --start_id 2 --num_stations 1 --ssid <ssid> --passwd <password> 
                    --security wpa2 --cleanup

STATUS: BETA RELEASE

VERIFIED_ON:   9-JUN-2023,
             GUI Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

            ''')
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--start_id',
        help='Specify the station starting id \n e.g: --start_id <value> default 0', 
        default=0)

    optional = parser.add_argument_group('Optional arguments')
    optional.add_argument(
        '--mode',
        help='Mode for your station (as a number)',
        default=0)
    optional.add_argument(
        '--station_flag',
        help='station flags to add. eg: --station_flag ht40_disable',
        required=False,
        default=None)

    optional.add_argument(
        "--radio_antenna",
        help='Number of spatial streams: \n'
            ' default = -1 \n'
            ' 0 Diversity (All) \n'
            ' 1 Fixed-A (1x1) \n'
            ' 4 AB (2x2) \n'
            ' 7 ABC (3x3) \n'
            ' 8 ABCD (4x4) \n'
            ' 9 (8x8) \n', 
        default='-1')
    optional.add_argument(
        "--radio_channel", 
        help='Radio Channel: \n'
            ' default: AUTO \n'
            ' e.g:   --radio_channel 6 (2.4G) \n'
                    '\t--radio_channel 36 (5G) \n',
        default='AUTO')
    optional.add_argument(
        "--radio_tx_power", 
        help='Radio tx-power \n'
            ' default: AUTO system defaults',
        default='AUTO')
    optional.add_argument(
        "--country_code",
        help='Radio Country Code:\n'
            'e.g: \t--country_code 840')
    optional.add_argument(
        "--no_pre_cleanup",
        help='Add this flag to stop cleaning up before station creation',
        action='store_true'
    )
    optional.add_argument(
        "--cleanup",
        help='Add this flag to clean up stations after creation',
        action='store_true'
    )

    args = parser.parse_args()

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    # if args.debug:
    #    pprint.pprint(args)
    #    time.sleep(5)
    if args.radio is None:
        raise ValueError("--radio required")

    start_id = 0
    if args.start_id != 0:
        start_id = int(args.start_id)

    num_sta = 2
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_stations_converted = int(args.num_stations)
        num_sta = num_stations_converted

    station_list = LFUtils.port_name_series(prefix="sta",
                                            start_id=start_id,
                                            end_id=start_id + num_sta - 1,
                                            padding_number=10000,
                                            radio=args.radio)

    print("station_list {}".format(station_list))

    create_station = CreateStation(_host=args.mgr,
                                   _port=args.mgr_port,
                                   _ssid=args.ssid,
                                   _password=args.passwd,
                                   _security=args.security,
                                   _sta_list=station_list,
                                   _sta_flags=args.station_flag,
                                   _mode=args.mode,
                                   _radio=args.radio,
                                   _set_txo_data=None,
                                   _proxy_str=args.proxy,
                                   _debug_on=args.debug)
    
    if(not args.no_pre_cleanup):
        create_station.cleanup()

    else:
        already_available_stations = create_station.get_station_list()
        if(len(already_available_stations) > 0):
            used_indices = [int(station_id.split('sta')[1]) for station_id in already_available_stations]
            for new_station in station_list:
                if(new_station in already_available_stations):
                    print('Some stations are already existing in the LANforge from the given start id.')
                    print('You can create stations from the start id {}'.format(max(used_indices) + 1))
                    exit(1)


    create_station.modify_radio(mgr=args.mgr, radio=args.radio, antenna=args.radio_antenna, channel=args.radio_channel,
                                tx_power=args.radio_tx_power, country_code=args.country_code)
    create_station.build()

    if(args.cleanup):
        create_station.cleanup()

    if create_station.passes():
        print('Created %s stations' % num_sta)
        create_station.exit_success()
    else:
        create_station.exit_fail()


if __name__ == "__main__":
    main()
