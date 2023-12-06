#!/usr/bin/env python3
'''
NAME: testgroup.py

PURPOSE:
    This script will create a test connection group in the LANforge GUI (Connection Group GUI tab).
     Test Groups are also referred to as Connection Groups.
     The script can preform the following tasks:
     - create a test group
     - add layer-3 cx's to a test group
     - remove layer-3 cx's from a test group
     - start and stop a test connection group


EXAMPLE:
    For an eth-to-eth test connection group (eth-to-eth Layer-3 connection must be manually created first):
        ./testgroup.py --mgr localhost --group_name eth_group --add_group --add_cx l3_eth_test --list_groups

    eth-to-eth JSON command example:
        "args":["--mgr","localhost",
                    "--group_name","eth_group",
                    "--add_group",
                    "--add_cx","l3_eth_test",
                    "--list_groups"
                    ]

    * Add multiple layer-3 cross-connections to a single connection group:
        ./testgroup.py --mgr localhost --group_name group1 --add_group --add_cx l3_test1,l3_test2 --list_groups --use_existing

    * Remove multiple layer-3 cx's from a connection group:
        ./testgroup.py --mgr 192.168.30.12 --group_name group1 --remove_cx l3_test1,l3_test2 --list_groups --use_existing

    * Add a single layer-3 cross connection to a connection group:
        ./testgroup.py --mgr localhost --group_name group1 --add_group --add_cx l3_test --list_groups --use_existing

    * Remove a layer-3 cx from a specified connection group:
        ./testgroup.py --mgr localhost --group_name group1 --remove_cx l3_test1 --list_groups --use_existing

    * Add single layer-3 cross-connections to a single connection group and strat group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --add_group --add_cx l3_test --start_group CX_GROUP --use_existing

    * Add multiple layer-3 cross-connections to a single connection group and strat group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --add_group --add_cx l3_test,l3_test1 --start_group CX_GROUP --use_existing

    * Start Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --start_group CX_GROUP --use_existing

    * Stop Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --stop_group CX_GROUP --use_existing

    * Quiesce Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --quiesce_group CX_GROUP --use_existing

    * Delete Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP1 --del_group --use_existing


    * To create given number of stations and l3 cross-connections along with add them in a test-group.

         ./testgroup.py --mgr 192.168.200.138 --num_stations 2 --ssid Netgear2g --passwd lanforge --security wpa2
         --radio wiphy0 --group_name group0 --add_group --upstream_port eth2 --a_min 6000 --b_min 6000


    * To create given number of stations and l3 cross-connections along with add them in a test-group & Start Selected Group:

        ./testgroup.py --mgr 192.168.200.138 --num_stations 2 --ssid Netgear2g --passwd lanforge --security wpa2
        --radio wiphy0 --group_name group0 --start_group group0


SCRIPT_CLASSIFICATION:  Creation, Addition, Deletion, Creation stations & test-groups

SCRIPT_CATEGORIES: Functional

STATUS: Functional

VERIFIED_ON:   7-AUG-2023,
             GUI Version:  5.4.6
             Kernel Version: 6.2.16+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
'''

import sys
import os
import importlib
import argparse
import time
import logging
import pprint

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

# lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
# LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class TestGroup(Realm):
    def __init__(self, host, port,
                 ssid=None,
                 security=None,
                 password=None,
                 sta_list=None,
                 name_prefix=None,
                 upstream=None,
                 radio=None,
                 mode=0,
                 ap=None,
                 _up=True,
                 number_template="00000",
                 use_ht160=False,
                 side_a_min_rate=56,
                 side_a_max_rate=0,
                 side_b_min_rate=56,
                 side_b_max_rate=0,
                 group_name=None,
                 add_cx_list=None,
                 rm_cx_list=None,
                 tg_action=None,
                 cx_action=None,
                 list_groups=None,
                 show_group=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False
                 ):
        super().__init__(lfclient_host=host, lfclient_port=port)

        if add_cx_list is None:
            add_cx_list = []
        self.rm_cx_list = rm_cx_list
        if rm_cx_list is None:
            rm_cx_list = []
        self.tg_profile = self.new_test_group_profile()
        # print(f"group_name:{group_name}, list_groups:{list_groups}, tg_action:{tg_action}, cx_action:{cx_action}, "
        #       f"add_cx_list:{add_cx_list}, rm_cx_list:{rm_cx_list}, show_group:{show_group}")
        if (group_name is None
                and list_groups is None
                and (tg_action is not None
                     or cx_action is not None
                     or add_cx_list is not None
                     or rm_cx_list is not None
                     or show_group is not None)):
            raise ValueError(
                "Group name must be set if manipulating test groups")
        elif group_name:
            self.tg_profile.group_name = group_name

        if add_cx_list:
            if len(add_cx_list) == 1 and ',' in add_cx_list[0]:
                self.add_cx_list = add_cx_list[0].split(',')
        else:
            self.add_cx_list = add_cx_list

        self.add_cx_list = add_cx_list
        if rm_cx_list:
            if len(rm_cx_list) == 1 and ',' in rm_cx_list[0]:
                self.rm_cx_list = rm_cx_list[0].split(',')
        else:
            self.rm_cx_list = rm_cx_list

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
        self.up = _up
        self.number_template = number_template
        self.debug = _debug_on
        self.name_prefix = name_prefix
        # why?
        self.station_profile = None
        self.cx_profile = None
        if self.sta_list and len(self.sta_list) >0:
            self.new_station_profile()
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
            # self.station_list= LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=2, padding_number_=10000, radio='wiphy0') #Make radio a user defined variable from terminal.

            self.cx_profile.host = self.host
            self.cx_profile.port = self.port
            self.cx_profile.name_prefix = self.name_prefix
            self.cx_profile.side_a_min_bps = side_a_min_rate
            self.cx_profile.side_a_max_bps = side_a_max_rate
            self.cx_profile.side_b_min_bps = side_b_min_rate
            self.cx_profile.side_b_max_bps = side_b_max_rate

        self.tg_action = tg_action
        self.cx_action = cx_action
        self.list_groups = list_groups
        self.show_group = show_group

    def pre_cleanup(self):
        if self.cx_profile:
            self.cx_profile.cleanup_prefix()
        if self.sta_list and len(self.sta_list) > 0:
            for sta in self.sta_list:
                self.rm_port(sta, check_exists=True)

    def build(self):
        # JBR: this step...did not calibrate if the Connection Group existed!
        if self.sta_list and self.ssid:
            print("testgroup::build: building sta_list...")
            pprint.pprint(["sta_list:", self.sta_list])
            raise ValueError("testgroup:build: requires ssid")
            self.station_profile.use_security(self.security,
                                              self.ssid,
                                              self.password)
            self.station_profile.set_number_template(self.number_template)
            print("Creating stations")
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param("set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
            # self.station_profile.create(radio=self.radio,
            #                             sta_names_=self.sta_list,
            #                             debug=self.debug)
            if self.station_profile.create(
                radio=self.radio,
                sta_names_=self.sta_list,
                debug=self.debug):
                self._pass("Stations created.")
            else:
                self._fail("Stations not properly created.")

        if self.sta_list and self.up:
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

        pprint.pprint(["testgroup::build: cx_profile", self.cx_profile])
        if self.cx_profile:
            self.cx_profile.create(endp_type="lf_udp",
                                   side_a=self.station_profile.station_names,
                                   side_b=self.upstream,
                                   sleep_time=0)
            self.add_cx_list = self.cx_profile.get_cx_names()
            self._pass("PASS: Cross Connection build finished")

    def do_cx_action(self):
        if self.cx_action == 'start':
            logger.info("Starting %s" % self.tg_profile.group_name)
            self.tg_profile.start_group()
        elif self.cx_action == 'stop':
            logger.info("Stopping %s" % self.tg_profile.group_name)
            self.tg_profile.stop_group()
        elif self.cx_action == 'quiesce':
            logger.info("Quiescing %s" % self.tg_profile.group_name)
            self.tg_profile.quiesce_group()

    def do_tg_action(self):
        if self.tg_action == 'add':
            logger.info("Creating %s" % self.tg_profile.group_name)
            self.tg_profile.create_group()
        if self.tg_action == 'del':
            logger.info("Removing %s" % self.tg_profile.group_name)
            if self.tg_profile.check_group_exists():
                self.tg_profile.rm_group()
            else:
                logger.info("%s not found, no action taken" % self.tg_profile.group_name)

    def show_info(self):
        time.sleep(.25)
        if self.list_groups:
            tg_list = self.tg_profile.list_groups()
            if len(tg_list) > 0:
                logger.info("Current Test Groups: %s" % tg_list)
                for group in tg_list:
                    print(f"{group} ")
                    logger.info(group)
            else:
                logger.info("testgroup::show_info: No test groups found")
        if self.show_group:
            cx_list = self.tg_profile.list_cxs()
            if len(cx_list) > 0:
                logger.info("Showing cxs in %s" % self.tg_profile.group_name)
                for cx in cx_list:
                    logger.info(cx)
            else:
                logger.info("No cxs found in %s" % self.tg_profile.group_name)

    def update_cxs(self):
        if len(self.add_cx_list) > 0:
            logger.info("Adding cxs %s to %s" % (', '.join(self.add_cx_list), self.tg_profile.group_name))
            print("CX LIST", self.add_cx_list)
            if type(self.add_cx_list) is list:
                cx_list = self.add_cx_list[0]
                split_cx_list = cx_list.split(',')
            else:
                split_cx_list = self.add_cx_list
            # for cx in self.add_cx_list:
            for cx in split_cx_list:
                self.tg_profile.add_cx(cx)
                self.tg_profile.cx_list.append(cx)
        if len(self.rm_cx_list) > 0:
            logger.info("Removing cxs %s from %s" % (', '.join(self.rm_cx_list), self.tg_profile.group_name))
            for cx in self.rm_cx_list:
                self.tg_profile.rm_cx(cx)
                if cx in self.tg_profile.cx_list:
                    self.tg_profile.cx_list.remove(cx)


def main():
    parser = Realm.create_basic_argparse(
        prog='testgroup.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Control and query test groups\n''',
        description='''
NAME: testgroup.py

PURPOSE:
    This script will create a test connection group in the LANforge GUI (Connection Group GUI tab).
     Test Groups are also referred to as Connection Groups.
     The script can preform the following tasks:
     - create a test group
     - add layer-3 cx's to a test group
     - remove layer-3 cx's from a test group
     - start and stop a test connection group


EXAMPLE:
    For an eth-to-eth test connection group (eth-to-eth Layer-3 connection must be manually created first):
        ./testgroup.py --mgr localhost --group_name eth_group --add_group --add_cx l3_eth_test --list_groups

    eth-to-eth JSON command example:
        "args":["--mgr","localhost",
                    "--group_name","eth_group",
                    "--add_group",
                    "--add_cx","l3_eth_test",
                    "--list_groups"
                    ]

    * Add multiple layer-3 cross-connections to a single connection group:
        ./testgroup.py --mgr localhost --group_name group1 --add_group --add_cx l3_test1,l3_test2 --list_groups --use_existing

    * Remove multiple layer-3 cx's from a connection group:
        ./testgroup.py --mgr 192.168.30.12 --group_name group1 --remove_cx l3_test1,l3_test2 --list_groups --use_existing

    * Add a single layer-3 cross connection to a connection group:
        ./testgroup.py --mgr localhost --group_name group1 --add_group --add_cx l3_test --list_groups --use_existing

    * Remove a layer-3 cx from a specified connection group:
        ./testgroup.py --mgr localhost --group_name group1 --remove_cx l3_test1 --list_groups --use_existing

    * Add single layer-3 cross-connections to a single connection group and strat group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --add_group --add_cx l3_test --start_group CX_GROUP --use_existing

    * Add multiple layer-3 cross-connections to a single connection group and strat group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --add_group --add_cx l3_test,l3_test1 --start_group CX_GROUP --use_existing

    * Start Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --start_group CX_GROUP --use_existing

    * Stop Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --stop_group CX_GROUP --use_existing

    * Quiesce Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP --quiesce_group CX_GROUP --use_existing

    * Delete Selected Group:

        ./testgroup.py --mgr 192.168.200.93 --group_name CX_GROUP1 --del_group --use_existing
        
        
    * To create given number of stations and l3 cross-connections along with add them in a test-group.
                
         ./testgroup.py --mgr 192.168.200.138 --num_stations 2 --ssid Netgear2g --passwd lanforge --security wpa2 
         --radio wiphy0 --group_name group0 --add_group --upstream_port eth2 --a_min 6000 --b_min 6000

    
    * To create given number of stations and l3 cross-connections along with add them in a test-group & Start Selected Group:

        ./testgroup.py --mgr 192.168.200.138 --num_stations 2 --ssid Netgear2g --passwd lanforge --security wpa2 
        --radio wiphy0 --group_name group0 --start_group group0


SCRIPT_CLASSIFICATION:  Creation, Addition, Deletion, Creation stations & test-groups

SCRIPT_CATEGORIES: Functional

STATUS: Functional

VERIFIED_ON:   7-AUG-2023,
             GUI Version:  5.4.6
             Kernel Version: 6.2.16+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
    ''')

    parser.add_argument('--a_min', help='--a_min bps rate minimum for side_a', default=256000)
    parser.add_argument('--b_min', help='--b_min bps rate minimum for side_b', default=256000)

    parser.add_argument('--mode', help='Used to force mode of stations')
    parser.add_argument('--ap', help='Used to force a connection to a particular AP')

    parser.add_argument(
        '--group_name', help='specify the name of the test group to use', default=None)
    parser.add_argument(
        '--list_groups', help='list all existing test groups', action='store_true', default=False)
    parser.add_argument(
        '--show_group', help='show connections in current test group', action='store_true', default=False)
    parser.add_argument(
        '--add_cx', help='add cx to chosen test group', nargs='*', default=[])
    parser.add_argument(
        '--remove_cx', help='remove cx from chosen test group', nargs='*', default=[])
    parser.add_argument('--use_existing', help='specify this to use already existed cx for connection group.',
                        action='store_true', default=False)

    tg_group = parser.add_mutually_exclusive_group()
    tg_group.add_argument(
        '--add_group', help='add new test group', action='store_true', default=False)
    tg_group.add_argument(
        '--del_group', help='delete test group', action='store_true', default=False)

    cx_group = parser.add_mutually_exclusive_group()
    cx_group.add_argument(
        '--start_group', help='start all cxs in chosen test group', default=None)
    cx_group.add_argument(
        '--stop_group', help='stop all cxs in chosen test group', default=None)
    cx_group.add_argument(
        '--quiesce_group', help='quiesce all cxs in chosen test groups', default=None)

    args = parser.parse_args()

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    num_sta = 0
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_sta = int(args.num_stations)

    station_list: list = []
    if num_sta > 0:
        station_list = LFUtils.portNameSeries(prefix_="sta",
                                              start_id_=0,
                                              end_id_=num_sta - 1,
                                              padding_number_=10000,
                                              radio=args.radio)

    tg_action = None
    cx_action = None

    if args.add_group:
        tg_action = 'add'
    elif args.del_group:
        tg_action = 'del'

    if args.start_group:
        cx_action = 'start'
    elif args.stop_group:
        cx_action = 'stop'
    elif args.quiesce_group:
        cx_action = 'quiesce'

    # Query the groups we have and determine if the name being provided already
    # exists, otherwise we affect an existing test group.
    testgrp = TestGroup(host=args.mgr,
                        port=args.mgr_port,
                        _debug_on=args.debug,
                        list_groups=True)
    testgrp.list_groups = True
    testgrp.do_tg_action()
    testgrp.show_info()

    # print(f"use_existing:{args.use_existing}, list_groups:{args.list_groups} "
    #       f"sta_list{station_list}\n")
    if not (args.list_groups or args.use_existing or args.num_stations):
        ip_var_test = TestGroup(host=args.mgr,
                                port=args.mgr_port,
                                number_template="0000",
                                sta_list=station_list,
                                name_prefix="VT-",
                                upstream=args.upstream_port,
                                ssid=args.ssid,
                                password=args.passwd,
                                radio=args.radio,
                                security=args.security,
                                use_ht160=False,
                                side_a_min_rate=args.a_min,
                                side_b_min_rate=args.b_min,
                                mode=args.mode,
                                ap=args.ap,
                                group_name=args.group_name,
                                tg_action=tg_action,
                                cx_action=cx_action,
                                _debug_on=args.debug)
        ip_var_test.pre_cleanup()
        ip_var_test.build()
        if not ip_var_test.passes():
            print(ip_var_test.get_fail_message())
            ip_var_test.exit_fail()
        ip_var_test.do_tg_action()
        ip_var_test.update_cxs()
        ip_var_test.do_cx_action()
        time.sleep(0.25)
        ip_var_test.show_info()
        print('Creates %s stations and connections' % num_sta)
    else:
        # print(f"args.list_groups:[{args.list_groups}]")
        tg = TestGroup(host=args.mgr, port=args.mgr_port,
                       group_name=args.group_name,
                       add_cx_list=args.add_cx,
                       rm_cx_list=args.remove_cx,
                       cx_action=cx_action,
                       tg_action=tg_action,
                       list_groups=args.list_groups,
                       show_group=args.show_group)
        tg.do_tg_action()
        tg.update_cxs()
        tg.do_cx_action()
        time.sleep(0.25)
        tg.show_info()


if __name__ == "__main__":
    main()
