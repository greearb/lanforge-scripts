#!/usr/bin/env python3
"""

 Create Layer-3 Cross Connection Using LANforge JSON API : https://www.candelatech.com/cookbook.php?vol=fire&book=scripted+layer-3+test
 Written by Candela Technologies Inc.

PURPOSE:
Supports creating user-specified Layer-3 cross-connection.
Supports regression testing for QA

 Example Command:

 For layer-3 cx creation on LANforge:
   ./create_l3.py --endp_a 'eth1' --endp_b 'eth2' --min_rate_a '56000' --min_rate_b '40000' --no_cleanup

For remote layer-3 cx creation:
   ./create_l3.py --mgr localhost --endp_a 'eth1' --endp_b 'eth2' --min_rate_a '56000' --min_rate_b '40000' --no_cleanup

 For regression (script will create the layer-3 cx, check if it was successful, and then remove the layer-3 cx):
  ./create_l3.py --endp_a 'eth1' --endp_b 'eth2' --min_rate_a '56000' --min_rate_b '40000'

For batch creation functionality:
  ./create_l3.py --mgr 192.168.200.93 --endp_a 'sta0000' --endp_b 'sta0001' --min_rate_a '6200000' --min_rate_b '6200000'
   --batch_creation --quantity 100 --endp_a_increment 0 --endp_b_increment 0 --ip_port_increment_a 1 --ip_port_increment_b 1
    --min_ip_port_b 2000 --multi_conn 1 --no_cleanup

Tested on 02/10/2023:
         kernel version: 5.19.17+
         gui version: 5.4.6
         the layer-3 scenario successfully created and tested was an eth-to-eth cross connection (eth1-to-eth2 on an APU2/ct521a).

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
                 host="localhost", port=8080, mode=0,
                 min_rate_a=56, max_rate_a=0,
                 min_rate_b=56, max_rate_b=0,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _batch_create=None,
                 _quantity=None,
                 _endp_a_increment=None,
                 _endp_b_increment=None,
                 _ip_port_increment_a=None,
                 _ip_port_increment_b=None,
                 _min_ip_port_a=None,
                 _min_ip_port_b=None,
                 _multi_conn=None):
        super().__init__(host, port)
        self.host = host
        self.port = port
        self.endp_b = endp_b
        self.endp_a = endp_a
        self.mode = mode
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
        self.cx_profile.mconn = _multi_conn
        # for batch creation window automation attributes
        self.batch_create =  _batch_create
        self.quantity = _quantity
        self.port_increment_a = _endp_a_increment
        self.port_increment_b = _endp_b_increment
        self.ip_port_increment_a = _ip_port_increment_a
        self.ip_port_increment_b = _ip_port_increment_b
        self.min_ip_port_a = _min_ip_port_a
        self.min_ip_port_b = _min_ip_port_b

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()

    def build(self):
        logger.info("Batch Creator: %s" % self.batch_create)
        if not self.batch_create:
            if self.cx_profile.create(endp_type="lf_udp",
                                      side_a=self.endp_a,
                                      side_b=self.endp_b,
                                      sleep_time=0):
                self._pass("Cross-connect build finished")
            else:
                self._fail("Cross-connect build did not succeed.")
        else:
            for i in range(int(self.quantity)):
                if self.cx_profile.create(endp_type="lf_udp",
                                          side_a=self.endp_a,
                                          side_b=self.endp_b,
                                          sleep_time=0, ip_port_a=self.min_ip_port_a, ip_port_b=self.min_ip_port_b):
                    # self.min_ip_port_a = int(self.min_ip_port_a) + int(self.ip_port_increment_a)
                    self.min_ip_port_b = int(self.min_ip_port_b) + int(self.ip_port_increment_b)
                    self._pass("Cross-connect build finished")
                else:
                    self._fail("Cross-connect build did not succeed.")


def main():
    parser = LFCliBase.create_basic_argparse(
        prog='create_l3.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Generate traffic between ports
            ''',
        description='''\
Create Layer-3 Cross Connection Using LANforge JSON API : https://www.candelatech.com/cookbook.php?vol=fire&book=scripted+layer-3+test

PURPOSE:
Supports creating user-specified Layer-3 cross-connection.
Supports regression testing for QA

Example Command:

For cross-connection creation:
   ./create_l3.py --endp_a 'eth1' --endp_b 'eth2' --min_rate_a '56000' --min_rate_b '40000' --no_cleanup
   ./create_l3.py --ssid lanforge --password password --security wpa2 --radio 1.1.wiphy0 --endp_a wiphy0 --endp_b wiphy1 --no_cleanup

For remote layer-3 cx creation:
   ./create_l3.py --mgr localhost --endp_a 'eth1' --endp_b 'eth2' --min_rate_a '56000' --min_rate_b '40000' --no_cleanup

For regression (script will create the layer-3 cx, check if it was successful, and then remove the layer-3 cx):
  ./create_l3.py --endp_a 'eth1' --endp_b 'eth2' --min_rate_a '56000' --min_rate_b '40000'

Tested on 02/10/2023:
         kernel version: 5.19.17+
         gui version: 5.4.6
         the layer-3 scenario successfully created and tested was an eth-to-eth cross connection (eth1-to-eth2 on an APU2/ct521a).

        ''')
    parser.add_argument(
        '--min_rate_a',
        help='--min_rate_a bps rate minimum for side_a',
        default=56000)
    parser.add_argument(
        '--min_rate_b',
        help='--min_rate_b bps rate minimum for side_b',
        default=56000)
    parser.add_argument(
        '--endp_a',
        help='--endp_a station list',
        default=[],
        action="append",
        required=True)
    parser.add_argument(
        '--endp_b',
        help='--upstream port',
        default="eth2",
        required=True)
    parser.add_argument(
        '--ap',
        help='Used to force a connection to a particular AP')
    parser.add_argument(
        '--number_template',
        help='Start the station numbering with a particular number. Default is 0000',
        default=0000)
    parser.add_argument('--mode', help='Used to force mode of stations')

    parser.add_argument('--min_ip_port_a', help='min ip port range for endp-a', default=-1)
    parser.add_argument('--min_ip_port_b', help='min ip port range for endp-b', default=-1)
    parser.add_argument('--multi_conn', help='modify multi connection for cx', default=0, type=int)
    parser.add_argument('--batch_creation', help='Enable the batch-creation to use the ip-port increment', action='store_true')
    parser.add_argument('--quantity', help='No of cx endp to create', default=1)
    parser.add_argument('--endp_a_increment', help='End point - A port increment', default=1)
    parser.add_argument('--endp_b_increment', help='End point - B port increment', default=1)
    parser.add_argument('--ip_port_increment_a', help='ip port increment for endp-a', default=1)
    parser.add_argument('--ip_port_increment_b', help='ip port increment for endp-b', default=1)
    args = parser.parse_args()

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    num_sta = 0
    # if (args.num_stations is not None) and (int(args.num_stations) > 0):
    #     num_sta = int(args.num_stations)

    ip_var_test = CreateL3(host=args.mgr,
                           port=args.mgr_port,
                           name_prefix="VT",
                           endp_a=args.endp_a,
                           endp_b=args.endp_b,
                           min_rate_a=args.min_rate_a,
                           min_rate_b=args.min_rate_b,
                           mode=args.mode,
                           _debug_on=args.debug,
                           _batch_create=args.batch_creation,
                           _quantity=args.quantity,
                           _endp_a_increment=args.endp_a_increment,
                           _endp_b_increment=args.endp_b_increment,
                           _ip_port_increment_a=args.ip_port_increment_a,
                           _ip_port_increment_b=args.ip_port_increment_b,
                           _min_ip_port_a=args.min_ip_port_a,
                           _min_ip_port_b=args.min_ip_port_b,
                           _multi_conn=args.multi_conn
                           )

    ip_var_test.pre_cleanup()

    ip_var_test.build()

    # TODO:  Delete the thing just created, unless --no_cleanup option was added.
    # Similar to how the create_bond.py does it.

    if not args.no_cleanup:
        ip_var_test.pre_cleanup()

    if ip_var_test.passes():
        logger.info("Created %s stations and connections" % num_sta)
        ip_var_test.exit_success()
    else:
        ip_var_test.exit_fail()


if __name__ == "__main__":

    main()
