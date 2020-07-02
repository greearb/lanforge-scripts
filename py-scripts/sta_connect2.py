#!/usr/bin/env python3

#  This will create a station, create TCP and UDP traffic, run it a short amount of time,
#  and verify whether traffic was sent and received.  It also verifies the station connected
#  to the requested BSSID if bssid is specified as an argument.
#  The script will clean up the station and connections at the end of the test.

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge import LFUtils
# from LANforge import LFCliBase
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
from realm import Realm

OPEN="open"
WEP="wep"
WPA="wpa"
WPA2="wpa2"
MODE_AUTO=0

class StaConnect2(LFCliBase):
    def __init__(self, host, port, _dut_ssid="MyAP", _dut_passwd="NA", _dut_bssid="",
                 _user="", _passwd="", _sta_mode="0", _radio="wiphy0",
                 _resource=1, _upstream_resource=1, _upstream_port="eth2",
                 _sta_name=None, _debugOn=False, _dut_security=OPEN, _exit_on_error=False,
                 _cleanup_on_exit=True, _runtime_sec=60, _exit_on_fail=False):
        # do not use `super(LFCLiBase,self).__init__(self, host, port, _debugOn)
        # that is py2 era syntax and will force self into the host variable, making you
        # very confused.
        super().__init__(host, port, _debug=_debugOn, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.debugOn = _debugOn
        self.dut_security = ""
        self.dut_ssid = _dut_ssid
        self.dut_passwd = _dut_passwd
        self.dut_bssid = _dut_bssid
        self.user = _user
        self.passwd = _passwd
        self.sta_mode = _sta_mode  # See add_sta LANforge CLI users guide entry
        self.radio = _radio
        self.resource = _resource
        self.upstream_resource = _upstream_resource
        self.upstream_port = _upstream_port
        self.runtime_secs = _runtime_sec
        self.cleanup_on_exit = _cleanup_on_exit
        self.sta_url_map = None  # defer construction
        self.upstream_url = None  # defer construction
        self.station_names = []
        if _sta_name is not None:
            self.station_names = [ _sta_name ]
        # self.localrealm :Realm = Realm(lfclient_host=host, lfclient_port=port) # py > 3.6
        self.localrealm = Realm(lfclient_host=host, lfclient_port=port) # py > 3.6
        self.resulting_stations = {}
        self.resulting_endpoints = {}

    # def get_realm(self) -> Realm: # py > 3.6
    def get_realm(self):
        return self.localrealm

    def get_station_url(self, sta_name_=None):
        if sta_name_ is None:
            raise ValueError("get_station_url wants a station name")
        if self.sta_url_map is None:
            self.sta_url_map = {}
            for sta_name in self.station_names:
                self.sta_url_map[sta_name] = "port/1/%s/%s" % (self.resource, sta_name)
        return self.sta_url_map[sta_name_]

    def get_upstream_url(self):
        if self.upstream_url is None:
            self.upstream_url = "port/1/%s/%s" % (self.upstream_resource, self.upstream_port)
        return self.upstream_url

    # Compare pre-test values to post-test values
    def compare_vals(self, name, postVal, print_pass=False, print_fail=True):
        # print(f"Comparing {name}")
        if postVal > 0:
            self._pass("%s %s" % (name, postVal), print_pass)
        else:
            self._fail("%s did not report traffic: %s" % (name, postVal), print_fail)

    def remove_stations(self):
        for name in self.station_names:
            LFUtils.removePort(self.resource, name, self.lfclient_url)

    def num_associated(self, bssid):
        counter = 0
        # print("there are %d results" % len(self.station_results))
        fields = "_links,port,alias,ip,ap,port+type"
        self.station_results = self.localrealm.find_ports_like("sta*", fields, debug_=False)
        if (self.station_results is None) or (len(self.station_results) < 1):
            self.get_failed_result_list()
        for eid,record in self.station_results.items():
            #print("-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- ")
            #pprint(eid)
            #pprint(record)
            if record["ap"] == bssid:
                counter += 1
            #print("-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- ")
        return counter

    def clear_test_results(self):
        self.resulting_stations = {}
        self.resulting_endpoints = {}
        super().clear_test_results()
        #super(StaConnect, self).clear_test_results().test_results.clear()

    def setup(self):
        self.clear_test_results()
        self.check_connect()
        upstream_json = self.json_get("%s?fields=alias,phantom,down,port,ip" % self.get_upstream_url(), debug_=False)

        if upstream_json is None:
            self._fail(message="Unable to query %s, bye" % self.upstream_port, print_=True)
            return False

        if upstream_json['interface']['ip'] == "0.0.0.0":
            pprint.pprint(upstream_json)
            self._fail("Warning: %s lacks ip address" % self.get_upstream_url(), print_=True)
            return False

        # remove old stations
        print("removing old station")
        for sta_name in self.station_names:
            sta_url = self.get_station_url(sta_name)
            response = self.json_get(sta_url)
            if response is not None:
                if response["interface"] is not None:
                    for sta_name in self.station_names:
                        LFUtils.removePort(self.resource, sta_name, self.lfclient_url)
                    LFUtils.wait_until_ports_disappear(self.resource, self.lfclient_url, self.station_names)

        # Create stations and turn dhcp on
        sta_profile = self.localrealm.new_station_profile()

        if self.dut_security == WPA2:
            sta_profile.use_wpa2(on=True, ssid=self.dut_ssid, passwd=self.dut_passwd)
        elif self.dut_security == OPEN:
            sta_profile.use_wpa2(on=False, ssid=self.dut_ssid)
        sta_profile.set_command_flag("add_sta", "create_admin_down", 1)

        print("Adding new stations ", end="")
        sta_profile.create(resource=self.resource, radio=self.radio, sta_names_=self.station_names)

        # Create endpoints and cxs
        # Create UDP endpoints

        l3_udp_profile = self.localrealm.new_l3_cx_profile()
        l3_udp_profile.side_a_min_bps = 128000
        l3_udp_profile.side_b_min_bps = 128000
        l3_udp_profile.side_a_min_pdu = 1200
        l3_udp_profile.side_b_min_pdu = 1500
        l3_udp_profile.report_timer = 1000
        l3_udp_profile.prefix = "udp_"
        l3_udp_profile.create(endp_type="lf_udp",
                          side_a=list(self.localrealm.find_ports_like("sta+")),
                          side_b="%d.%s" % (self.resource, self.upstream_port))

        # Create TCP endpoints

        l3_tcp_profile = self.localrealm.new_l3_cx_profile()
        l3_tcp_profile.side_a_min_bps = 128000
        l3_tcp_profile.side_b_min_bps = 56000
        l3_tcp_profile.prefix = "tcp_"
        l3_tcp_profile.report_timer = 1000


    def start(self):
        # print("\nBringing ports up...")
        # data = {"shelf": 1,
        #         "resource": self.resource,
        #         "port": "ALL",
        #         "probe_flags": 1}
        # self.json_post("/cli-json/nc_show_ports", data)
        # LFUtils.waitUntilPortsAdminUp(self.resource, self.lfclient_url, self.station_names)

        # station_info = self.jsonGet(self.mgr_url, "%s?fields=port,ip,ap" % (self.getStaUrl()))
        duration = 0
        maxTime = 300
        ip = "0.0.0.0"
        ap = ""
        print("Waiting for %s stations to associate to AP: " % len(self.station_names), end="")
        connected_stations = {}
        # while (len(connected_stations.keys()) < len(self.station_names)) and (duration < maxTime):
        #     duration += 3
        #     time.sleep(3)
        #     print(".", end="")
        #     for sta_name in self.station_names:
        #         sta_url = self.get_station_url(sta_name)
        #         station_info = self.json_get(sta_url + "?fields=port,ip,ap")
        #
        #         # LFUtils.debug_printer.pprint(station_info)
        #         if (station_info is not None) and ("interface" in station_info):
        #             if "ip" in station_info["interface"]:
        #                 ip = station_info["interface"]["ip"]
        #             if "ap" in station_info["interface"]:
        #                 ap = station_info["interface"]["ap"]
        #
        #         if (ap == "Not-Associated") or (ap == ""):
        #             if self.debugOn:
        #                 print(" -%s," % sta_name, end="")
        #         else:
        #             if ip == "0.0.0.0":
        #                 if self.debugOn:
        #                     print(" %s (0.0.0.0)" % sta_name, end="")
        #             else:
        #                 connected_stations[sta_name] = sta_url
        #     data = {
        #         "shelf":1,
        #         "resource": self.resource,
        #         "port": "ALL",
        #         "probe_flags": 1
        #     }
        #     self.json_post("/cli-json/nc_show_ports", data)

        # make a copy of the connected stations for test records


        for sta_name in self.station_names:
            sta_url = self.get_station_url(sta_name)
            station_info = self.json_get(sta_url) # + "?fields=port,ip,ap")
            if station_info is None:
                print("unable to query %s" % sta_url)
            self.resulting_stations[sta_url] = station_info
            ap = station_info["interface"]["ap"]
            ip = station_info["interface"]["ip"]
            if (ap != "") and (ap != "Not-Associated"):
                print(" %s +AP %s, " % (sta_name, ap), end="")
                if self.dut_bssid != "":
                    if self.dut_bssid.lower() == ap.lower():
                        self._pass(sta_name+" connected to BSSID: " + ap)
                        # self.test_results.append("PASSED: )
                        # print("PASSED: Connected to BSSID: "+ap)
                    else:
                        self._fail("%s connected to wrong BSSID, requested: %s  Actual: %s" % (sta_name, self.dut_bssid, ap))
            else:
                self._fail(sta_name+" did not connect to AP")
                return False

            if ip == "0.0.0.0":
                self._fail("%s did not get an ip. Ending test" % sta_name)
            else:
                self._pass("%s connected to AP: %s  With IP: %s" % (sta_name, ap, ip))

        if self.passes() == False:
            if self.cleanup_on_exit:
                print("Cleaning up...")
                self.remove_stations()
            return False


        # start cx traffic
        print("\nStarting CX Traffic")
        # for cx_name in cx_names.keys():
        #     data = {
        #         "test_mgr": "ALL",
        #         "cx_name": cx_name,
        #         "cx_state": "RUNNING"
        #     }
        #     self.json_post("/cli-json/set_cx_state", data)

        # Refresh stats

        print("Refresh CX stats")
        # for cx_name in cx_names.keys():
        #     data = {
        #         "test_mgr": "ALL",
        #         "cross_connect": cx_name
        #     }
        #     self.json_post("/cli-json/show_cxe", data)

    def stop(self):
        # stop cx traffic
        print("Stopping CX Traffic")
        # for cx_name in cx_names.keys():
        #     data = {
        #         "test_mgr": "ALL",
        #         "cx_name": cx_name,
        #         "cx_state": "STOPPED"
        #     }
        #     self.json_post("/cli-json/set_cx_state", data)

        # Refresh stats
        print("\nRefresh CX stats")
        # for cx_name in cx_names.keys():
        #     data = {
        #         "test_mgr": "ALL",
        #         "cross_connect": cx_name
        #     }
        #     self.json_post("/cli-json/show_cxe", data)

        # print("Sleeping for 5 seconds")
        time.sleep(5)

        # get data for endpoints JSON
        print("Collecting Data")
        # for cx_name in cx_names.keys():
        #     try:
        #         # ?fields=tx+bytes,rx+bytes
        #         endp_url = "/endp/%s" % cx_names[cx_name]["a"]
        #         ptest = self.json_get(endp_url)
        #         self.resulting_endpoints[endp_url] = ptest
        #
        #         ptest_a_tx = ptest['endpoint']['tx bytes']
        #         ptest_a_rx = ptest['endpoint']['rx bytes']
        #
        #         #ptest = self.json_get("/endp/%s?fields=tx+bytes,rx+bytes" % cx_names[cx_name]["b"])
        #         endp_url = "/endp/%s" % cx_names[cx_name]["b"]
        #         ptest = self.json_get(endp_url)
        #         self.resulting_endpoints[endp_url] = ptest
        #
        #         ptest_b_tx = ptest['endpoint']['tx bytes']
        #         ptest_b_rx = ptest['endpoint']['rx bytes']
        #
        #         self.compare_vals("testTCP-A TX", ptest_a_tx)
        #         self.compare_vals("testTCP-A RX", ptest_a_rx)
        #
        #         self.compare_vals("testTCP-B TX", ptest_b_tx)
        #         self.compare_vals("testTCP-B RX", ptest_b_rx)
        #
        #     except Exception as e:
        #         self.error(e)

        # Examples of what happens when you add test results that do not begin with PASS
        # self.test_results.append("Neutral message will fail")
        # self.test_results.append("FAILED message will fail")
        # print("\n")

    def cleanup(self):
        # remove all endpoints and cxs
        if self.cleanup_on_exit:
            for sta_name in self.station_names:
                LFUtils.removePort(self.resource, sta_name, self.lfclient_url)
            endp_names = []
            removeCX(self.lfclient_url, cx_names.keys())
            for cx_name in cx_names:
                endp_names.append(cx_names[cx_name]["a"])
                endp_names.append(cx_names[cx_name]["b"])
            removeEndps(self.lfclient_url, endp_names)

# ~class


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    parser = argparse.ArgumentParser(
        description="""LANforge Unit Test:  Connect Station to AP
Example:
./sta_connect2.py --dest 192.168.100.209 --dut_ssid OpenWrt-2 --dut_bssid 24:F5:A2:08:21:6C
""")
    parser.add_argument("-d", "--dest", type=str, help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-u", "--user", type=str, help="TBD: credential login/username")
    parser.add_argument("-p", "--passwd", type=str, help="TBD: credential password")
    parser.add_argument("--resource", type=str, help="LANforge Station resource ID to use, default is 1")
    parser.add_argument("--upstream_resource", type=str, help="LANforge Ethernet port resource ID to use, default is 1")
    parser.add_argument("--upstream_port", type=str, help="LANforge Ethernet port name, default is eth2")
    parser.add_argument("--radio", type=str, help="LANforge radio to use, default is wiphy0")
    parser.add_argument("--sta_mode", type=str,
                        help="LANforge station-mode setting (see add_sta LANforge CLI documentation, default is 0 (auto))")
    parser.add_argument("--dut_ssid", type=str, help="DUT SSID")
    parser.add_argument("--dut_passwd", type=str, help="DUT PSK password.  Do not set for OPEN auth")
    parser.add_argument("--dut_bssid", type=str, help="DUT BSSID to which we expect to connect.")

    args = parser.parse_args()
    if args.dest is not None:
        lfjson_host = args.dest
    if args.port is not None:
        lfjson_port = args.port

    staConnect = StaConnect2(lfjson_host, lfjson_port)
    staConnect.station_names = [ "sta0000" ]
    if args.user is not None:
        staConnect.user = args.user
    if args.passwd is not None:
        staConnect.passwd = args.passwd
    if args.sta_mode is not None:
        staConnect.sta_mode = args.sta_mode
    if args.upstream_resource is not None:
        staConnect.upstream_resource = args.upstream_resource
    if args.upstream_port is not None:
        staConnect.upstream_port = args.upstream_port
    if args.radio is not None:
        staConnect.radio = args.radio
    if args.resource is not None:
        staConnect.resource = args.resource
    if args.dut_passwd is not None:
        staConnect.dut_passwd = args.dut_passwd
    if args.dut_bssid is not None:
        staConnect.dut_bssid = args.dut_bssid
    if args.dut_ssid is not None:
        staConnect.dut_ssid = args.dut_ssid

    staConnect.setup()
    staConnect.start()

    time.sleep(staConnect.runtime_secs)
    staConnect.stop()
    run_results = staConnect.get_result_list()
    is_passing = staConnect.passes()
    if is_passing == False:
        print("FAIL:  Some tests failed")
    else:
        print("PASS:  All tests pass")
    print(staConnect.get_all_message())

    staConnect.cleanup()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
    main()
