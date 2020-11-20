#!/usr/bin/env python3

import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

# import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from LANforge import LFUtils
from LANforge import add_file_endp
from LANforge.add_file_endp import *
import argparse
import realm
import time
import datetime


class FileIOTest(LFCliBase):
    def __init__(self, host, port, ssid, security, password,
                 number_template="00000",
                 radio="wiphy0",
                 fs_type=fe_fstype.EP_FE_NFS4.name,
                 min_rw_size=64*1024,
                 max_rw_size=64*1024,
                 min_file_size=25*1024*1024,
                 max_file_size=25*1024*1024,
                 min_read_rate_bps=1000*1000,
                 max_read_rate_bps=1000*1000,
                 min_write_rate_bps="1G",
                 max_write_rate_bps=1000*1000,
                 directory="AUTO",
                 test_duration="5m",
                 upstream_port="eth1",
                 num_ports=1,
                 server_mount="10.40.0.1:/var/tmp/test",
                 macvlan_parent=None,
                 first_mvlan_ip=None,
                 netmask=None,
                 gateway=None,
                 dhcp=True,
                 use_macvlans=False,
                 port_list=[],
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.radio = radio
        self.upstream_port = upstream_port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.number_template = number_template
        self.test_duration = test_duration
        self.sta_list = []
        self.use_macvlans = use_macvlans
        if self.use_macvlans:
            if macvlan_parent != None:
                self.macvlan_parent = macvlan_parent
                self.port_list = port_list
        else:
            self.sta_list = port_list
        #self.min_rw_size = self.parse_size(min_rw_size)
        #self.max_rw_size = self.parse_size(max_rw_size)
        #self.min_file_size = self.parse_size(min_file_size)
        #self.min_file_size = self.parse_size(min_file_size)
        #self.min_read_rate_bps = self.parse_size_bps(min_read_rate_bps)
        #self.max_read_rate_bps = self.parse_size_bps(max_read_rate_bps)
        #self.min_write_rate_bps = self.parse_size_bps(min_write_rate_bps)
        #self.max_write_rate_bps = self.parse_size_bps(max_write_rate_bps)

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.endp_profile = self.local_realm.new_fio_endp_profile()
        self.mvlan_profile = self.local_realm.new_mvlan_profile()

        if len(self.sta_list) > 0:
            self.station_profile = self.local_realm.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = self.ssid
            self.station_profile.ssid_pass = self.password
            self.station_profile.security = self.security
            self.station_profile.number_template_ = self.number_template
            self.station_profile.mode = 0

        self.endp_profile.fs_type = fs_type
        self.endp_profile.min_rw_size = LFUtils.parse_size(min_rw_size)
        self.endp_profile.max_rw_size = LFUtils.parse_size(max_rw_size)
        self.endp_profile.min_file_size = LFUtils.parse_size(min_file_size)
        self.endp_profile.min_file_size = LFUtils.parse_size(min_file_size)
        self.endp_profile.min_read_rate_bps = LFUtils.parse_size(min_read_rate_bps)
        self.endp_profile.max_read_rate_bps = LFUtils.parse_size(max_read_rate_bps)
        self.endp_profile.min_write_rate_bps = LFUtils.parse_size(min_write_rate_bps)
        self.endp_profile.max_write_rate_bps = LFUtils.parse_size(max_write_rate_bps)
        self.endp_profile.directory = directory
        self.endp_profile.server_mount = server_mount

        self.ro_profile = self.endp_profile.create_ro_profile()

        self.mvlan_profile.num_macvlans = int(num_ports)
        self.mvlan_profile.desired_macvlans = self.port_list
        self.mvlan_profile.macvlan_parent = self.macvlan_parent
        self.mvlan_profile.dhcp = dhcp
        self.mvlan_profile.netmask = netmask
        self.mvlan_profile.first_ip_addr = first_mvlan_ip
        self.mvlan_profile.gateway = gateway

        self.created_ports = []
    def __compare_vals(self, val_list):
        passes = 0
        expected_passes = 0
        # print(val_list)
        for item in val_list:
            expected_passes += 1
            # print(item)
            if item[0] == 'r':
                # print("TEST", item,
                #       val_list[item]['read-bps'],
                #       self.endp_profile.min_read_rate_bps,
                #       val_list[item]['read-bps'] > self.endp_profile.min_read_rate_bps)

                if val_list[item]['read-bps'] > self.endp_profile.min_read_rate_bps:
                    passes += 1
            else:
                # print("TEST", item,
                #       val_list[item]['write-bps'],
                #       self.endp_profile.min_write_rate_bps,
                #       val_list[item]['write-bps'] > self.endp_profile.min_write_rate_bps)

                if val_list[item]['write-bps'] > self.endp_profile.min_write_rate_bps:
                    passes += 1
            if passes == expected_passes:
                return True
            else:
                return False
        else:
            return False

    def __get_values(self):
        time.sleep(3)
        cx_list = self.json_get("fileio/%s,%s?fields=write-bps,read-bps" % (','.join(self.endp_profile.created_cx.keys()), ','.join(self.ro_profile.created_cx.keys())),
                                debug_=self.debug)
        # print(cx_list)
        # print("==============\n", cx_list, "\n==============")
        cx_map = {}
        if cx_list is not None:
            cx_list = cx_list['endpoint']
            for i in cx_list:
                for item, value in i.items():
                    # print(item, value)
                    cx_map[self.local_realm.name_to_eid(item)[2]] = {"read-bps": value['read-bps'], "write-bps": value['write-bps']}
        # print(cx_map)
        return cx_map

    def build(self):
        # Build stations
        # print(self.min_tx_bps, self.min_rx_bps)
        # TODO: Check for upstream port as child to bridge before macvlan create
        if self.use_macvlans:
            self.mvlan_profile.create(admin_down=True, sleep_time=.5, debug=self.debug)
            self.created_ports += self.mvlan_profile.created_macvlans

        if len(self.sta_list) > 0:
            self.station_profile.use_security(self.security, self.ssid, self.password)
            self.station_profile.set_number_template(self.number_template)
            print("Creating stations")
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param("set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
            self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
            self._pass("PASS: Station build finished")
            self.created_ports += self.station_profile.station_names


        self.endp_profile.create(ports=self.created_ports, sleep_time=.5, debug_=self.debug,
                                 suppress_related_commands_=None)
        self.ro_profile.create(ports=self.created_ports, sleep_time=.5, debug_=self.debug,
                               suppress_related_commands_=None)

    def start(self, print_pass=False, print_fail=False):
        temp_ports = self.port_list.copy()
        #temp_stas.append(self.local_realm.name_to_eid(self.upstream_port)[2])
        self.station_profile.admin_up()
        self.mvlan_profile.admin_up()
        exit(1)
        if self.local_realm.wait_for_ip(temp_ports):
            self._pass("All ports got IPs", print_pass)
        else:
            self._fail("Ports failed to get IPs", print_fail)
        cur_time = datetime.datetime.now()
        # print("Got Values")
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.endp_profile.start_cx()
        time.sleep(2)
        self.ro_profile.start_cx()
        passes = 0
        expected_passes = 0
        print("Starting Test...")
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(seconds=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)

            new_rx_values = self.__get_values()
            # exit(1)
            # print(new_rx_values)
            # print("\n-----------------------------------")
            # print(cur_time, end_time, cur_time + datetime.timedelta(minutes=1))
            # print("-----------------------------------\n")
            expected_passes += 1
            if self.__compare_vals(new_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
                # break
            # old_rx_values = new_rx_values
            cur_time = datetime.datetime.now()
        if passes == expected_passes:
            self._pass("PASS: All tests passes", print_pass)

    def stop(self):
        self.endp_profile.stop_cx()
        self.ro_profile.stop_cx()
        self.station_profile.admin_down()
        self.mvlan_profile.admin_down()

    def cleanup(self, sta_list=None):
        self.endp_profile.cleanup()
        self.ro_profile.cleanup()
        if len(self.sta_list) > 0:
            self.station_profile.cleanup(sta_list)
            LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=sta_list, debug=self.debug)
        self.mvlan_profile.cleanup()


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    parser = LFCliBase.create_basic_argparse(
        prog='test_fileio.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Creates FileIO endpoints which can be NFS, CIFS or iSCSI endpoints.''',

        description='''\
test_fileio.py:
--------------------
Generic command layout:
python ./test_fileio.py --upstream_port <port> --radio <radio 0> <stations> <ssid> <ssid password> <security type: wpa2, open, wpa3> --debug

python3 ./test_fileio.py --upstream_port eth1 --fio_type fe_nfs4 --min_read 1Mbps --min_write 1Gbps --server_mount 192.168.93.195:/tmp/test
''')

    parser.add_argument('--test_duration', help='sets the duration of the test', default="5m")
    parser.add_argument('--fs_type', help='endpoint type', default="fe_nfs4")
    parser.add_argument('--min_rw_size', help='minimum read/write size', default=64*1024)
    parser.add_argument('--max_rw_size', help='maximum read/write size', default=64*1024)
    parser.add_argument('--min_file_size', help='minimum file size', default=50*1024*1024)
    parser.add_argument('--max_file_size', help='maximum file size', default=50*1024*1024)
    parser.add_argument('--min_read_rate_bps', help='minimum bps read rate', default=10e9)
    parser.add_argument('--max_read_rate_bps', help='maximum bps read rate', default=10e9)
    parser.add_argument('--min_write_rate_bps', help='minimum bps write rate', default=10e9)
    parser.add_argument('--max_write_rate_bps', help='maximum bps write rate', default="1G")
    parser.add_argument('--directory', help='--directory directory to read/write in. Absolute path suggested', default="AUTO")
    parser.add_argument('--server_mount', help='--server_mount The server to mount, ex: 192.168.100.5/exports/test1',
                        default="10.40.0.1:/var/tmp/test")
    parser.add_argument('--macvlan_parent', help='specifies parent port for macvlan creation', default=None)
    parser.add_argument('--first_port', help='specifies name of first port to be used', default=None)
    parser.add_argument('--num_ports', help='number of ports to create', default=1)
    parser.add_argument('--use_macvlans', help='will create macvlans', action='store_true', default=False)
    parser.add_argument('--first_mvlan_ip', help='specifies first static ip address to be used or dhcp', default=None)
    parser.add_argument('--netmask', help='specifies netmask to be used with static ip addresses', default=None)
    parser.add_argument('--gateway', help='specifies default gateway to be used with static addressing', default=None)
    args = parser.parse_args()

    port_list = []
    if args.first_port is not None:
        if args.first_port.startswith("sta"):
            if (args.num_ports is not None) and (int(args.num_ports) > 0):
                start_num = int(args.first_port[4:])
                num_ports = int(args.num_ports)
                port_list = LFUtils.port_name_series(prefix="sta", start_id=start_num, end_id=start_num+num_ports-1,
                                                   padding_number=10000,
                                                   radio=args.radio)
        else:
            if (args.num_ports is not None) and args.macvlan_parent is not None and (int(args.num_ports) > 0) \
                                            and args.macvlan_parent in args.first_port:
                start_num = int(args.first_port[args.first_port.index('#')+1:])
                num_ports = int(args.num_ports)
                port_list = LFUtils.port_name_series(prefix=args.macvlan_parent+"#", start_id=start_num,
                                                   end_id=start_num+num_ports-1, padding_number=100000,
                                                   radio=args.radio)
            else:
                raise ValueError("Invalid values for num_ports [%s], macvlan_parent [%s], and/or first_port [%s].\n"
                                 "first_port must contain parent port and num_ports must be greater than 0"
                                 % (args.num_ports, args.macvlan_parent, args.first_port))
    else:
        num_ports = int(args.num_ports)
        if not args.use_macvlans:
            port_list = LFUtils.port_name_series(prefix="sta", start_id=0, end_id=num_ports - 1,
                                               padding_number=10000,
                                               radio=args.radio)
        else:
            port_list = LFUtils.port_name_series(prefix=args.macvlan_parent + "#", start_id=0,
                                               end_id=num_ports - 1, padding_number=100000,
                                               radio=args.radio)
    if args.first_mvlan_ip.lower() == "dhcp":
        dhcp = True
    else:
        dhcp = False
    print(port_list)

    ip_test = FileIOTest(args.mgr,
                         args.mgr_port,
                         ssid=args.ssid,
                         password=args.passwd,
                         security=args.security,
                         port_list=port_list,
                         test_duration=args.test_duration,
                         upstream_port=args.upstream_port,
                         _debug_on=args.debug,

                         macvlan_parent=args.macvlan_parent,
                         use_macvlans=args.use_macvlans,
                         first_mvlan_ip=args.first_mvlan_ip,
                         netmask=args.netmask,
                         gateway=args.gateway,
                         dhcp=dhcp,
                         fs_type=args.fs_type,
                         min_rw_size=args.min_rw_size,
                         max_rw_size=args.max_rw_size,
                         min_file_size=args.min_file_size,
                         max_file_size=args.max_file_size,
                         min_read_rate_bps=args.min_read_rate_bps,
                         max_read_rate_bps=args.max_read_rate_bps,
                         min_write_rate_bps=args.min_write_rate_bps,
                         max_write_rate_bps=args.max_write_rate_bps,
                         directory=args.directory,
                         server_mount=args.server_mount,
                         num_ports=args.num_ports
                         # want a mount options param
                         )

    ip_test.cleanup(port_list)
    ip_test.build()
    if not ip_test.passes():
        print(ip_test.get_fail_message())
        exit(1)
    ip_test.start(False, False)
    ip_test.stop()
    if not ip_test.passes():
        print(ip_test.get_fail_message())
        # exit(1)
    time.sleep(30)
    ip_test.cleanup(port_list)
    if ip_test.passes():
        print("Full test passed, all endpoints had increased bytes-rd throughout test duration")


if __name__ == "__main__":
    main()
