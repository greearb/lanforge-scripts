#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')
import LANforge
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm
import time


class IPv4Test(LFCliBase):
    def __init__(self, host, port, ssid, security, password, sta_list=None, num_stations=0, prefix="00000", _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.num_stations = num_stations
        self.sta_list = sta_list
        self.timeout = 120
        self.prefix = prefix
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                            security=self.security, prefix=self.prefix, mode=0, up=True, dhcp=True,
                                            debug_=False)

    def build(self):
        # Build stations
        self.profile.use_wpa2(True, self.ssid, self.password)
        self.profile.set_prefix(self.prefix)
        print("Creating stations")
        self.profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=False)

    def start(self):
        # Bring stations up
        for sta_name in self.sta_list:
            data = LFUtils.portUpRequest(1, sta_name)
            url = "json-cli/set_port"
            print(sta_name)
            self.json_post(url, data)


    def stop(self):
        # Bring stations down
        for sta_name in self.sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "json-cli/set_port"
            print(sta_name)
            self.json_post(url, data)

    def run_test(self, sta_list, print_pass=False, print_fail=False):
        associated_map = {}
        ip_map = {}
        for sec in range(self.timeout):
            for sta_name in sta_list:
                sta_status = self.json_get("port/1/1/" + sta_name + "?fields=port,alias,ip,ap")
                # print(sta_status)
                if sta_status is None or sta_status['interface'] is None or sta_status['interface']['ap'] is None:
                    continue
                if len(sta_status['interface']['ap']) == 17 and sta_status['interface']['ap'][-3] == ':':
                    # print("Associated", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map[sta_name] = 1
                if len(sta_status['interface']['ap']) == 17 and sta_status['interface']['ap'][-3] == ':' \
                        and sta_status['interface']['ip'] != '0.0.0.0':
                    # print("IP", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map[sta_name] = 1
                    ip_map[sta_name] = 1

            time.sleep(1)
        # print(len(sta_list), sta_list)
        # print(len(ip_map), ip_map)
        # print(len(associated_map), associated_map)
        if (len(sta_list) == len(ip_map)) and (len(sta_list) == len(associated_map)):
            self._pass("PASS: All stations associated with IP", print_pass)
        else:
            self._fail("FAIL: Not all stations able to associate/get IP", print_fail)
            print(sta_list)
            print(ip_map)
            print(associated_map)

        return self.passes()

    def cleanup(self):
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
                "resource": 1,
                "port": sta_name
            }
            # print(data)
            self.json_post(req_url, data)

    def run(self):
        if len(self.sta_list) == 0:
            sta_list = []
            for sta_name in list(self.local_realm.find_ports_like("sta[%s..%s]" % (
                    self.prefix, str(self.prefix[:-len(str(self.num_stations))]) + str(self.num_stations - 1)))):
                sta_list.append(self.local_realm.name_to_eid(sta_name)[2])


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=5, padding_number_=10000)
    ip_test = IPv4Test(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                       security="open", sta_list=station_list)
    ip_test.cleanup()
    ip_test.timeout = 60
    ip_test.build()
    ip_test.start()
    print("Full Test Passed: %s" % ip_test.run_test(ip_test.sta_list))
    ip_test.stop()
    time.sleep(30)
    ip_test.start()
    time.sleep(30)
    ip_test.cleanup()


if __name__ == "__main__":
    main()
