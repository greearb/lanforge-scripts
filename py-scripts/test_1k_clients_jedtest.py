#!/usr/bin/env python3
import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

import os

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
from realm import Realm
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import argparse

class Test1KClients(LFCliBase):
    def __init__(self,
                 host,
                 port,
                 num_sta_=200,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host,
                         port,
                         _debug=_debug_on,
                         _local_realm=Realm(lfclient_host=host, lfclient_port=port),
                         _halt_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail)
        self.ssid_radio_map = {
            '1.1.wiphy0' : ("wpa2", "jedway-wpa2-x2048-4-4", "jedway-wpa2-x2048-4-4"),
            '1.1.wiphy1' : ("wpa2", "jedway-wpa2-x2048-5-1", "jedway-wpa2-x2048-5-1"),
            '1.1.wiphy2' : ("wpa2", "jedway-wpa2-x2048-4-1", "jedway-wpa2-x2048-4-1"),

            '1.2.wiphy0' : ("wpa2", "jedway-wpa2-x2048-5-3", "jedway-wpa2-x2048-5-3"),
            '1.2.wiphy1' : ("wpa2", "jedway-wpa2-x2048-4-4", "jedway-wpa2-x2048-4-4"),
            '1.2.wiphy2' : ("wpa2", "jedway-wpa2-x2048-4-1", "jedway-wpa2-x2048-4-1"),
        }
        if num_sta_ is None:
            raise ValueError("need a number of stations per radio")
        self.num_sta = int(num_sta_)

        self.station_radio_map = {
            # port_name_series(prefix=prefix_, start_id=start_id_, end_id=end_id_, padding_number=padding_number_, radio=radio)
            "1.1.wiphy0" : LFUtils.port_name_series(start_id=0,    end_id=self.num_sta-1,      padding_number=10000, radio="1.1.wiphy0"),
            "1.1.wiphy1" : LFUtils.port_name_series(start_id=1000, end_id=1000+self.num_sta-1, padding_number=10000, radio="1.1.wiphy1"),
            "1.1.wiphy2" : LFUtils.port_name_series(start_id=2000, end_id=2000+self.num_sta-1, padding_number=10000, radio="1.1.wiphy2"),

            "1.2.wiphy0" : LFUtils.port_name_series(start_id=3000, end_id=3000+self.num_sta-1, padding_number=10000, radio="1.2.wiphy0"),
            "1.2.wiphy1" : LFUtils.port_name_series(start_id=4000, end_id=4000+self.num_sta-1, padding_number=10000, radio="1.2.wiphy1"),
            "1.2.wiphy2" : LFUtils.port_name_series(start_id=5000, end_id=5000+self.num_sta-1, padding_number=10000, radio="1.2.wiphy2")
        }
        self.station_profile_map = {}

    def build(self):
        for (radio, name_series) in self.station_radio_map.items():
            print("building stations for %s"%radio)
            if (name_series is None) or len(name_series) < 1:
                print("No name series for %s"%radio)
                continue
            station_profile = self.local_realm.new_station_profile()
            station_profile.use_security(self.ssid_radio_map[radio][0],
                                         self.ssid_radio_map[radio][1],
                                         self.ssid_radio_map[radio][2])
            self.station_profile_map[radio] = station_profile

        self._pass("defined %s station profiles" % len(self.station_radio_map))
        for (radio, station_profile) in self.station_profile_map.items():
            station_profile.create(self, radio,
                                   sta_names_=self.station_radio_map[radio],
                                   dry_run=False,
                                   up_=False,
                                   debug=self.debug,
                                   suppress_related_commands_=True,
                                   use_radius=False,
                                   hs20_enable=False,
                                   sleep_time=2)
            self.local_realm.wait_until_ports_appear(self.station_radio_map[radio])

        self._pass("built stations on %s radios" % len(self.station_radio_map))

    def start(self):
        print("bringing stations up")
        for (radio, station_profile) in self.station_profile_map.items():
            station_profile.admin_up()
            if self.local_realm.wait_for_ip(station_list=self.station_radio_map[radio], debug=self.debug, timeout_sec=90):
                self._pass("stations on radio %s up" % radio)
            else:
                self._fail("stations on radio %s are still down" % radio)
                exit(1)

    def stop(self):
        pass

    def cleanup(self):
        #for (radio, station_list) in self.station_radio_map.items():
        self.local_realm.remove_all_stations(1)
        self.local_realm.remove_all_stations(2)


def main():
    num_sta=200
    lfjson_host = "localhost"
    lfjson_port = 8080

    argparser = LFCliBase.create_basic_argparse(prog=__file__,
                                                description="creates lots of stations across multiple radios",
                                                formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument("--sta_per_radio",
                           type=int,
                           help="number of stations per radio")

    args = argparser.parse_args()

    kilo_test = Test1KClients(lfjson_host,
                              lfjson_port,
                              num_sta_=args.sta_per_radio)
    kilo_test.cleanup()
    kilo_test.build()
    if not kilo_test.passes():
        print("test fails")
        exit(1)

    kilo_test.start()
    if not kilo_test.passes():
        print("test fails")
        exit(1)

    kilo_test.stop()
    if not kilo_test.passes():
        print("test fails")
        exit(1)
    kilo_test.cleanup()

if __name__ == "__main__":
    main()
