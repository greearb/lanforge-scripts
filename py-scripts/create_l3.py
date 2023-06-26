#!/usr/bin/env python3
"""
NAME: create_l3.py

PURPOSE: This script is used to create the user-specified Layer-3 cross-connection.

EXAMPLE:
        # For layer-3 cx creation on LANforge:

            ./create_l3.py --mgr localhost --endp_a eth1 --endp_b eth2 --min_rate_a 56000 --min_rate_b 40000 --no_cleanup

        # For remote layer-3 cx creation:

            ./create_l3.py --mgr localhost --endp_a eth1 --endp_b eth2 --min_rate_a 56000 --min_rate_b 40000
             --multi_conn_a 1 --multi_conn_b 1 --no_cleanup

        # For regression (script will create the layer-3 cx, check if it was successful, and then remove the layer-3 cx):

            ./create_l3.py --mgr localhost --endp_a 1.1.sta0000 --endp_b 1.2.sta0000 --min_rate_a 56000 --min_rate_b 40000 --no_cleanup

        # For batch creation functionality:
        (If the specified endpoints are not present in the port manager,the cross-connects will be in a PHANTOM state.)

            ./create_l3.py --mgr 192.168.200.93 --endp_a 1.1.eth1 --endp_b 1.1.wlan2 --min_rate_a 6200000 --min_rate_b 6200000
             --batch_quantity 10 --endp_a_increment 0 --endp_b_increment 1 --min_ip_port_a 1000 --min_ip_port_b 2000 
             --ip_port_increment_a 1 --ip_port_increment_b 1 --multi_conn_a 1 --multi_conn_b 1 --no_cleanup

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        Create Layer-3 Cross Connection Using LANforge JSON API : https://www.candelatech.com/cookbook.php?vol=fire&book=scripted+layer-3+test
        Written by Candela Technologies Inc.

        * Supports only creating user-specified Layer-3 cross-connection.
        * Supports regression testing for QA

        * If the specified ports used for creating endpoints are not present in the port manager, the cross-connects will be in a PHANTOM state.

STATUS: BETA RELEASE

VERIFIED_ON:   20-JUN-2023,
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
TestGroupProfile = realm.TestGroupProfile
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class CreateL3(Realm):
    def __init__(self,
                 name_prefix,
                 endp_b,
                 endp_a,
                 cx_type,
                 tos=None,
                 pkts_to_send=None,
                 host="localhost", port=8080,
                 min_rate_a=56, max_rate_a=0,
                 min_rate_b=56, max_rate_b=0,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
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
        self.host = host
        self.port = port
        self.endp_b = endp_b
        if endp_a:
            self.endp_a = endp_a[0].split(',')
        self.cx_type = cx_type
        self.tos = tos
        self.pkts_to_send = pkts_to_send
        self.name_prefix = name_prefix
        # self.station_profile = self.new_station_profile()
        # self.station_profile.lfclient_url = self.lfclient_url
        # self.station_list= LFUtils.portNameSeries(prefix_="sta", start_id_=0,
        # end_id_=2, padding_number_=10000, radio='wiphy0') #Make radio a user
        # defined variable from terminal.
        self.cx_profile = self.new_l3_cx_profile()
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = min_rate_a
        self.cx_profile.side_a_max_bps = max_rate_a
        self.cx_profile.side_b_min_bps = min_rate_b
        self.cx_profile.side_b_max_bps = max_rate_b
        self.cx_profile.mconn_A = _multi_conn_a
        self.cx_profile.mconn_B = _multi_conn_b
        # for batch creation window automation attributes
        self.batch_quantity = _quantity
        self.port_increment_a = _endp_a_increment
        self.port_increment_b = _endp_b_increment
        self.ip_port_increment_a = _ip_port_increment_a
        self.ip_port_increment_b = _ip_port_increment_b
        self.min_ip_port_a = _min_ip_port_a
        self.min_ip_port_b = _min_ip_port_b

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()

    def build(self):
        if self.cx_profile.create(endp_type=self.cx_type,
                                  side_a=self.endp_a,
                                  side_b=self.endp_b,
                                  sleep_time=0,
                                  tos=self.tos,
                                  pkts_to_send=self.pkts_to_send,
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


def main():
    parser = argparse.ArgumentParser(
        prog='create_l3.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Used for creating layer-3 cross connections
            ''',
        description='''\
NAME: create_l3.py

PURPOSE: This script is used to create the user-specified Layer-3 cross-connection.

EXAMPLE:
        # For layer-3 cx creation on LANforge:

            ./create_l3.py --mgr localhost --endp_a eth1 --endp_b eth2 --min_rate_a 56000 --min_rate_b 40000 --no_cleanup

        # For remote layer-3 cx creation:

            ./create_l3.py --mgr localhost --endp_a eth1 --endp_b eth2 --min_rate_a 56000 --min_rate_b 40000
             --multi_conn_a 1 --multi_conn_b 1 --no_cleanup

        # For regression (script will create the layer-3 cx, check if it was successful, and then remove the layer-3 cx):

            ./create_l3.py --mgr localhost --endp_a 1.1.sta0000 --endp_b 1.2.sta0000 --min_rate_a 56000 --min_rate_b 40000 --no_cleanup

        # For batch creation functionality:
        (If the specified endpoints are not present in the port manager,the cross-connects will be in a PHANTOM state.)

            ./create_l3.py --mgr 192.168.200.93 --endp_a 1.1.eth1 --endp_b 1.1.wlan2 --min_rate_a 6200000 --min_rate_b 6200000
             --batch_quantity 10 --endp_a_increment 0 --endp_b_increment 1 --min_ip_port_a 1000 --min_ip_port_b 2000 
             --ip_port_increment_a 1 --ip_port_increment_b 1 --multi_conn_a 1 --multi_conn_b 1 --no_cleanup

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        Create Layer-3 Cross Connection Using LANforge JSON API : https://www.candelatech.com/cookbook.php?vol=fire&book=scripted+layer-3+test
        Written by Candela Technologies Inc.

        * Supports only creating user-specified Layer-3 cross-connection.
        * Supports regression testing for QA

        * If the specified ports used for creating endpoints are not present in the port manager, the cross-connects will be in a PHANTOM state.

STATUS: BETA RELEASE

VERIFIED_ON:   20-JUN-2023,
             Build Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
''')

    parser.add_argument('--mgr', help='give the host ip')
    parser.add_argument('--mgr_port', default=8080, help='port LANforge GUI HTTP service is running on')
    parser.add_argument('--min_rate_a', help='--min_rate_a bps rate minimum for side_a', default=56000)
    parser.add_argument('--min_rate_b', help='--min_rate_b bps rate minimum for side_b', default=56000)
    parser.add_argument('--endp_a', help='--endp_a station list', default=[], action="append", required=True)
    parser.add_argument('--endp_b', help='--upstream port', default="eth2", required=True)
    parser.add_argument('--cx_type', help='specify the type of cx', default="lf_udp")
    parser.add_argument('--tos', help='specify tos for endpoints eg : BK | BE | VI | VO | Voice | Video')
    parser.add_argument('--pkts_to_send',
                        help='specify the pkts to send to the endpoints eg :One - 1 | Ten - 10 | (100) - 100 | (1000) - 1000')
    parser.add_argument('--multi_conn_a', help='modify multi connection endpoint-a for cx', default=0, type=int)
    parser.add_argument('--multi_conn_b', help='modify multi connection endpoint-b for cx', default=0, type=int)
    parser.add_argument('--min_ip_port_a', help='min ip port range for endp-a', default=-1)
    parser.add_argument('--min_ip_port_b', help='min ip port range for endp-b', default=-1)
    parser.add_argument('--batch_quantity', help='No of cx endpoints to batch-create', default=1)
    parser.add_argument('--endp_a_increment', help='End point - A port increment', default=0)
    parser.add_argument('--endp_b_increment', help='End point - B port increment', default=0)
    parser.add_argument('--ip_port_increment_a', help='ip port increment for endp-a', default=1)
    parser.add_argument('--ip_port_increment_b', help='ip port increment for endp-b', default=1)
    parser.add_argument('--no_cleanup', help='Do not cleanup before exit', action='store_true')
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument('--lf_logger_config_json',
                        help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--debug', '-d', default=False, action="store_true", help='Enable debugging')
    args = parser.parse_args()

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    ip_var_test = CreateL3(host=args.mgr,
                           port=args.mgr_port,
                           name_prefix="VT",
                           endp_a=args.endp_a,
                           endp_b=args.endp_b,
                           tos=args.tos,
                           cx_type=args.cx_type,
                           pkts_to_send=args.pkts_to_send,
                           min_rate_a=args.min_rate_a,
                           min_rate_b=args.min_rate_b,
                           _debug_on=args.debug,
                           _quantity=args.batch_quantity,
                           _endp_a_increment=args.endp_a_increment,
                           _endp_b_increment=args.endp_b_increment,
                           _ip_port_increment_a=args.ip_port_increment_a,
                           _ip_port_increment_b=args.ip_port_increment_b,
                           _min_ip_port_a=args.min_ip_port_a,
                           _min_ip_port_b=args.min_ip_port_b,
                           _multi_conn_a=args.multi_conn_a,
                           _multi_conn_b=args.multi_conn_b
                           )

    ip_var_test.pre_cleanup()

    ip_var_test.build()

    # TODO:  Delete the thing just created, unless --no_cleanup option was added.
    # Similar to how the create_bond.py does it.

    if not args.no_cleanup:
        ip_var_test.pre_cleanup()

    if ip_var_test.passes():
        logger.info("Cross Connects created successfully.")
        ip_var_test.exit_success()
    else:
        ip_var_test.exit_fail()


if __name__ == "__main__":
    main()
