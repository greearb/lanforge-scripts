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

    def cleanup(self):
        layer4_list = self.json_get("layer4/list?fields=name")
        print(layer4_list)

        if layer4_list is not None and 'endpoint' in layer4_list:
            if layer4_list['endpoint'] is not None:

                for name in self.sta_list:
                    req_url = "cli-json/rm_cx"
                    data = {
                        "test_mgr": "default_tm",
                        "cx_name": "CX_" + name + "_l4"
                    }
                    self.json_post(req_url, data, True)

                time.sleep(5)
                for endps in list(layer4_list['endpoint']):
                    for name, info in endps.items():
                        print(name)

                        req_url = "cli-json/rm_endp"
                        data = {
                            "endp_name": name
                        }
                        self.json_post(req_url, data, True)

        port_list = self.local_realm.station_list()
        sta_list = []
        for item in list(port_list):
            # print(list(item))
            if "sta" in list(item)[0]:
                sta_list.append(self.local_realm.name_to_eid(list(item)[0])[2])

        for sta_name in sta_list:
            req_url = "cli-json/rm_vlan"
            data = {
                "shelf": 1,
                "resource": self.resource,
                "port": sta_name
            }
            self.json_post(req_url, data, self.debug)
            time.sleep(.05)
        LFUtils.wait_until_ports_disappear(resource_id=self.resource, base_url=self.lfclient_url, port_list=sta_list,
                                           debug=self.debug)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)
    ip_test = IPV4L4(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                     security="open", station_list=station_list, url="dl http://localhost:8080/ /dev/null",
                     requests_per_ten=600)
    ip_test.cleanup()
    ip_test.build()
    ip_test.start()
    ip_test.cleanup()

if __name__ == "__main__":
    main()