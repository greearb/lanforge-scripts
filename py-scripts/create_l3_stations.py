#!/usr/bin/env python3
# flake8: noqa

"""
NAME: create_l3_stations.py

PURPOSE:
          ->  This script creates variable number of stations with individual cross-connects and endpoints.
              Stations are set to UP state, but cross-connections remain stopped.

          ->  This script support Batch-create Functionality.

EXAMPLE:
        Default configuration:
            Endpoint A: List of stations (default: 2 stations, unless specified with --num_stations)
            Endpoint B: eth1

        * Creating specified number of station names and Layer-3 CX :

            ./create_l3_stations.py --mgr localhost --num_stations 5 --radio wiphy0 --ssid SSID --password Password@123 --security wpa2

        * Creating stations with specified start ID (--num_template) and Layer-3 CX :

            ./create_l3_stations.py --mgr localhost --number_template 007 --radio wiphy0 --ssid SSID --password Password@123 --security wpa2

        * Creating stations with specified names and Layer-3 CX :

            ./create_l3_stations.py --mgr localhost --station_list sta00,sta01 --radio wiphy0 --ssid SSID --password Password@123 --security wpa2

        * For creating stations and layer-3 cx creation on particular specified AP mac & mode:

            ./create_l3_stations.py --mgr localhost --radio wiphy0 --ssid SSID --password Password@123 --security wpa2 --ap "00:0e:8e:78:e1:76"
            --mode 13

        * For creating specified number of stations and layer-3 cx creation (Customise the traffic and upstream port):

            ./create_l3_stations.py --mgr localhost --station_list sta00  --radio wiphy0 --ssid SSID --password Password@123 --security wpa2
             --upstream_port eth2 --min_rate_a 6200000 --min_rate_b 6200000

        * For Batch-Create :

            ./create_l3_stations.py --mgr 192.168.200.93 --endp_a 1.1.eth2 --endp_b 1.1.sta0002 --min_rate_a 6200000 --min_rate_b 6200000
            --batch_create --batch_quantity 8 --endp_a_increment 0 --endp_b_increment 0 --min_ip_port_a 1000 --min_ip_port_b 2000
            --ip_port_increment_a 1 --ip_port_increment_b 1 --multi_conn_a 1 --multi_conn_b 1

      Generic command layout:

        python3 ./create_l3_stations.py
            --upstream_port eth1
            --radio wiphy0
            --num_stations 32
            --security {open|wep|wpa|wpa2|wpa3}
            --ssid netgear
            --password admin123
            --min_rate_a 1000
            --min_rate_b 1000
            --ap "00:0e:8e:78:e1:76"
            --number_template 0000
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
                "bgnAX"  : "13",
            --debug

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        Create Layer-3 Cross Connection Using LANforge JSON API : https://www.candelatech.com/cookbook.php?vol=fire&book=scripted+layer-3+test
        Written by Candela Technologies Inc.

        * Supports creating of stations and creates Layer-3 cross-connection with the endpoint_A as stations created and endpoint_B as upstream port.
        * Supports regression testing for QA

STATUS: Functional

VERIFIED_ON:   27-JUN-2023,
             Build Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
"""

import sys
import os
import importlib
import argparse
import logging

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LANforge = importlib.import_module("py-json.LANforge")
lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class CreateL3(Realm):
    def __init__(
            self,
            ssid,
            security,
            password,
            sta_list,
            name_prefix,
            upstream,
            radio,
            host="localhost",
            port=8080,
            mode=0,
            ap=None,
            side_a_min_rate=56,
            side_a_max_rate=0,
            side_b_min_rate=56,
            side_b_max_rate=0,
            number_template="00000",
            use_ht160=False,
            _debug_on=False,
            _exit_on_error=False,
            _exit_on_fail=False,
            _endp_a=None,
            _endp_b=None,
            _batch_create=False,
            _quantity=None,
            _endp_a_increment=None,
            _endp_b_increment=None,
            _ip_port_increment_a=None,
            _ip_port_increment_b=None,
            _min_ip_port_a=None,
            _min_ip_port_b=None,
            _multi_conn_a=None,
            _multi_conn_b=None):
        super().__init__(host, port)
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.radio = radio
        self.mode = mode
        self.ap = ap
        self.number_template = number_template
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.endp_a = _endp_a
        self.endp_b = _endp_b
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.debug = self.debug
        self.station_profile.use_ht160 = use_ht160
        if self.station_profile.use_ht160:
            self.station_profile.mode = 9
        self.station_profile.mode = mode
        if self.ap is not None:
            self.station_profile.set_command_param("add_sta", "ap", self.ap)
        # self.station_list= LFUtils.portNameSeries(prefix_="sta", start_id_=0,
        # end_id_=2, padding_number_=10000, radio='wiphy0') #Make radio a user
        # defined variable from terminal.

        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate
        self.cx_profile.mconn_A = _multi_conn_a
        self.cx_profile.mconn_B = _multi_conn_b
        # for batch creation window automation attributes
        self.batch_create = _batch_create
        self.batch_quantity = _quantity
        self.port_increment_a = _endp_a_increment
        self.port_increment_b = _endp_b_increment
        self.ip_port_increment_a = _ip_port_increment_a
        self.ip_port_increment_b = _ip_port_increment_b
        self.min_ip_port_a = _min_ip_port_a
        self.min_ip_port_b = _min_ip_port_b

    def pre_cleanup(self):
        logger.info('pre_cleanup')
        self.cx_profile.cleanup_prefix()
        for sta in self.sta_list:
            self.rm_port(sta, check_exists=True, debug_=False)

    def build(self):
        if self.batch_create:  # Batch Create Functionality
            if self.cx_profile.create(endp_type="lf_udp",
                                      side_a=self.endp_a,
                                      side_b=self.endp_b,
                                      sleep_time=0,
                                      ip_port_a=self.min_ip_port_a,
                                      ip_port_b=self.min_ip_port_b,
                                      batch_quantity=self.batch_quantity,
                                      port_increment_a=self.port_increment_a,
                                      port_increment_b=self.port_increment_b,
                                      ip_port_increment_a=self.ip_port_increment_a,
                                      ip_port_increment_b=self.ip_port_increment_b
                                      ):
                self._pass("Cross-connect build finished")
            else:
                self._fail("Cross-connect build did not succeed.")
        else:  # Creating Stations along with Cross-connects
            self.station_profile.use_security(security_type=self.security,
                                              ssid=self.ssid,
                                              passwd=self.password)
            self.station_profile.set_number_template(self.number_template)
            logger.info("Creating stations")
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param(
                "set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)

            sta_timeout = 300
            # sta_timeout=3 # expect this to fail
            rv = self.station_profile.create(radio=self.radio,
                                             sta_names_=self.sta_list,
                                             debug=self.debug,
                                             timeout=sta_timeout)
            if not rv:
                self._fail("create_l3_stations: could not create all ports, exiting with error.")
            else:
                self._pass("Station creation succeeded.")
                self.start()
                cx_timeout = 300
                # cx_timeout=0 # expect this to fail
                rv = self.cx_profile.create(endp_type="lf_udp",
                                            side_a=self.station_profile.station_names,
                                            side_b=self.upstream,
                                            sleep_time=0,
                                            timeout=cx_timeout)
                if rv:
                    self._pass("CX creation finished")
                else:
                    self._fail("create_l3_stations: could not create all cx/endpoints.")

    def start(self):
        logger.info("Bringing up stations")
        self.admin_up(self.upstream)
        for sta in self.station_profile.station_names:
            logger.info("Bringing up station %s" % sta)
            self.admin_up(sta)

    def stop(self):
        logger.info("Bringing down stations")
        # self.admin_up(self.upstream)
        for sta in self.station_profile.station_names:
            logger.info("Bringing down station %s" % sta)
            self.admin_down(sta)

    def cleanup(self):
        logger.info("Clean up stations")
        self.cx_profile.cleanup_prefix()
        for sta in self.sta_list:
            self.rm_port(sta, check_exists=True, debug_=False)


def main():
    help_summary = '''\
    This script creates a variable number of stations with individual cross-connects and endpoints.
    The stations are initially set to the UP state, but the cross-connections are kept in a stopped state. It also 
    supports batch creation functionality, making it convenient to generate multiple stations at once.
    
    The script will creates stations & CX only, will not run/start traffic and will not generate any report.
        '''
    parser = LFCliBase.create_basic_argparse(
        prog='create_l3_stations.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations to test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open)
            ''',

        description='''\
"""
NAME: create_l3_stations.py

PURPOSE:
          ->  This script creates variable number of stations with individual cross-connects and endpoints.
              Stations are set to UP state, but cross-connections remain stopped.

          ->  This script support Batch-create Functionality.

EXAMPLE:
        Default configuration:
            Endpoint A: List of stations (default: 2 stations, unless specified with --num_stations)
            Endpoint B: eth1

        * Creating specified number of station names and Layer-3 CX :

            ./create_l3_stations.py --mgr localhost --num_stations 5 --radio wiphy0 --ssid SSID --password Password@123 --security wpa2

        * Creating stations with specified start ID (--num_template) and Layer-3 CX :

            ./create_l3_stations.py --mgr localhost --number_template 007 --radio wiphy0 --ssid SSID --password Password@123 --security wpa2

        * Creating stations with specified names and Layer-3 CX :

            ./create_l3_stations.py --mgr localhost --station_list sta00,sta01 --radio wiphy0 --ssid SSID --password Password@123 --security wpa2

        * For creating stations and layer-3 cx creation on particular specified AP mac & mode:

            ./create_l3_stations.py --mgr localhost --radio wiphy0 --ssid SSID --password Password@123 --security wpa2 --ap "00:0e:8e:78:e1:76"
            --mode 13

        * For creating specified number of stations and layer-3 cx creation (Customise the traffic and upstream port):

            ./create_l3_stations.py --mgr localhost --station_list sta00  --radio wiphy0 --ssid SSID --password Password@123 --security wpa2
             --upstream_port eth2 --min_rate_a 6200000 --min_rate_b 6200000

        * For Batch-Create :

            ./create_l3_stations.py --mgr 192.168.200.93 --endp_a 1.1.eth2 --endp_b 1.1.sta0002 --min_rate_a 6200000 --min_rate_b 6200000
            --batch_create --batch_quantity 8 --endp_a_increment 0 --endp_b_increment 0 --min_ip_port_a 1000 --min_ip_port_b 2000
            --ip_port_increment_a 1 --ip_port_increment_b 1 --multi_conn_a 1 --multi_conn_b 1

      Generic command layout:

        python3 ./create_l3_stations.py
            --upstream_port eth1
            --radio wiphy0
            --num_stations 32
            --security {open|wep|wpa|wpa2|wpa3}
            --ssid netgear
            --password admin123
            --min_rate_a 1000
            --min_rate_b 1000
            --ap "00:0e:8e:78:e1:76"
            --number_template 0000
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
                "bgnAX"  : "13",
            --debug

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        Create Layer-3 Cross Connection Using LANforge JSON API : https://www.candelatech.com/cookbook.php?vol=fire&book=scripted+layer-3+test
        Written by Candela Technologies Inc.

        * Supports creating of stations and creates Layer-3 cross-connection with the endpoint_A as stations created and endpoint_B as upstream port.
        * Supports regression testing for QA

STATUS: Functional

VERIFIED_ON:   27-JUN-2023,
             Build Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

''')

    parser.add_argument(
        '--min_rate_a',
        help='--min_rate_a bps rate minimum for side_a',
        default=256000)
    parser.add_argument(
        '--min_rate_b',
        help='--min_rate_b bps rate minimum for side_b',
        default=256000)
    parser.add_argument(
        '--mode', help='Used to force mode of stations')
    parser.add_argument(
        '--ap', help='Used to force a connection to a particular AP')
    parser.add_argument(
        '--number_template',
        help='Start the station numbering with a particular number. Default is 0000',
        default=0000)
    parser.add_argument(
        '--station_list',
        help='Optional: User defined station names, can be a comma or space separated list',
        nargs='+',
        default=None)
    # For batch_create
    parser.add_argument('--batch_create', help='To enable batch create functionality', action='store_true')

    parser.add_argument('--batch_quantity', help='No of cx endpoints to batch-create', default=1)
    parser.add_argument('--endp_a', help='--endp_a station list', default=[], action="append")
    parser.add_argument('--endp_b', help='--upstream port', default="eth2")
    parser.add_argument('--multi_conn_a', help='Modify multi connection endpoint-a for cx', default=0, type=int)
    parser.add_argument('--multi_conn_b', help='Modify multi connection endpoint-b for cx', default=0, type=int)
    parser.add_argument('--min_ip_port_a', help='Min ip port range for endp-a', default=-1)
    parser.add_argument('--min_ip_port_b', help='Min ip port range for endp-b', default=-1)
    parser.add_argument('--endp_a_increment', help='End point - A port increment', default=0)
    parser.add_argument('--endp_b_increment', help='End point - B port increment', default=0)
    parser.add_argument('--ip_port_increment_a', help='Ip port increment for endp-a', default=1)
    parser.add_argument('--ip_port_increment_b', help='Ip port increment for endp-b', default=1)
    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    num_sta = 2
    if args.num_stations:
        num_sta = int(args.num_stations)
    elif args.station_list:
        num_sta = len(args.station_list)

    if not args.station_list:
        station_list = LFUtils.portNameSeries(
            prefix_="sta", start_id_=int(
                args.number_template), end_id_=num_sta + int(
                args.number_template) - 1, padding_number_=10000, radio=args.radio)
    else:
        if ',' in args.station_list[0]:
            station_list = args.station_list[0].split(',')
        elif ' ' in args.station_list[0]:
            station_list = args.station_list[0].split()
        else:
            station_list = args.station_list
    ip_var_test = CreateL3(host=args.mgr, port=args.mgr_port, number_template=str(args.number_template),
                           sta_list=station_list, name_prefix="VT", upstream=args.upstream_port, ssid=args.ssid,
                           password=args.passwd, radio=args.radio, security=args.security, side_a_min_rate=args.min_rate_a,
                           side_b_min_rate=args.min_rate_b, mode=args.mode, ap=args.ap, _debug_on=args.debug,
                           _batch_create=args.batch_create, _endp_a=args.endp_a, _endp_b=args.endp_b, _quantity=args.batch_quantity,
                           _endp_a_increment=args.endp_a_increment,  _endp_b_increment=args.endp_b_increment,
                           _ip_port_increment_a=args.ip_port_increment_a, _ip_port_increment_b=args.ip_port_increment_b,
                           _min_ip_port_a=args.min_ip_port_a, _min_ip_port_b=args.min_ip_port_b,
                           _multi_conn_a=args.multi_conn_a, _multi_conn_b=args.multi_conn_b)

    if not args.no_cleanup:
        ip_var_test.pre_cleanup()
    ip_var_test.build()

    # TODO:  Do cleanup by default, allow --no_cleanup option to skip cleanup.

    if ip_var_test.passes():
        logger.info("Created %s stations and connections" % num_sta)
        ip_var_test.exit_success()
    else:
        ip_var_test.exit_fail()

if __name__ == "__main__":
    main()
