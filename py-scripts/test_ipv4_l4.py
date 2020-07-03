#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from LANforge import LFUtils
import realm
import time
import datetime


class IPV4L4(LFCliBase):
    def __init__(self, host, port, ssid, security, password, url, requests_per_ten, station_list, prefix="00000",
                 resource=1,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.url = url
        self.requests_per_ten = requests_per_ten
        self.prefix = prefix
        self.sta_list = station_list
        self.resource = resource

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                            security=self.security, number_template_=self.prefix, mode=0, up=False,
                                            dhcp=True,
                                            debug_=False)
        self.cx_profile = realm.L4CXProfile(lfclient_host=self.host, lfclient_port=self.port,
                                            local_realm=self.local_realm, debug_=False)
        self.cx_profile.url = self.url
        self.cx_profile.requests_per_ten = self.requests_per_ten

    def build(self):
        # Build stations
        self.profile.use_wpa2(True, self.ssid, self.password)
        self.profile.set_number_template(self.prefix)
        print("Creating stations")
        self.profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.profile.set_command_param("set_port", "report_timer", 1500)
        self.profile.set_command_flag("set_port", "rpt_timer", 1)
        self.profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=False)
        self._pass("PASS: Station build finished")
        temp_sta_list = []
        for station in range(len(self.sta_list)):
            temp_sta_list.append(str(self.resource) + "." + self.sta_list[station])

        self.cx_profile.create(ports=temp_sta_list, sleep_time=.5, debug_=False, suppress_related_commands_=None)

    def start(self):
        self.profile.admin_up(1)

    def stop(self):
        pass

    def cleanup(self, resource):
        pass


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)
    ip_test = IPV4L4(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                     security="open", station_list=station_list, url="http://localhost", requests_per_ten=600)
    ip_test.build()

if __name__ == "__main__":
    main()