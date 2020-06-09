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
import LANforge.lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *

OPEN="open"
WEP="wep"
WPA="wpa"
WPA2="wpa"
MODE_AUTO=0

class StaConnect(LFCliBase):
    def __init__(self, host, port, _dut_ssid="MyAP", _dut_passwd="NA", _dut_bssid="",
                 _user="", _passwd="", _sta_mode="0", _radio="wiphy0",
                 _resource=1, _upstream_resource=1, _upstream_port="eth2",
                 _sta_name=None, _debugOn=False, _dut_security=OPEN):
        # do not use `super(LFCLiBase,self).__init__(self, host, port, _debugOn)
        # that is py2 era syntax and will force self into the host variable, making you
        # very confused.
        super().__init__(host, port, _debug=_debugOn, _halt_on_error=False)
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
        # self.sta_name = _sta_name

        self.sta_url_map = None  # defer construction
        self.upstream_url = None  # defer construction
        self.station_names = []
        if _sta_name is not None:
            self.station_names = [ _sta_name ]

    def get_station_url(self, sta_name_=None):
        if sta_name_ is None:
            raise ValueError("get_station_url wants a station name")
        if self.sta_url_map is None:
            for sta_name in self.station_names:
                self.sta_url_map[sta_name] = "port/1/%s/%s" % (self.resource, self.sta_name)
        return self.sta_url_map[sta_name_]

    def getUpstreamUrl(self):
        if self.upstream_url is None:
            self.upstream_url = "port/1/%s/%s" % (self.upstream_resource, self.upstream_port)
        return self.upstream_url

    # Compare pre-test values to post-test values
    def compareVals(self, name, postVal, print_pass=False, print_fail=True):
        # print(f"Comparing {name}")
        if postVal > 0:
            self._pass("%s %s" % (name, postVal), print_pass)
        else:
            self._fail("%s did not report traffic: %s" % (name, postVal), print_fail)

    def remove_stations(self):
        for name in self.station_names:
            LFUtils.removePort(self.resource, name, self.lfclient_url)

    def run(self):
        self.clear_test_results()
        self.check_connect()
        eth1IP = self.json_get(self.getUpstreamUrl())
        if eth1IP is None:
            self._fail("Unable to query %s, bye" % self.upstream_port, True)
            return False
        if eth1IP['interface']['ip'] == "0.0.0.0":
            self._fail("Warning: %s lacks ip address" % self.getUpstreamUrl())
            return False

        for sta_name in self.station_names:
            sta_url = self.get_station_url(sta_name)
            response = self.json_get(sta_url)
            if response is not None:
                if response["interface"] is not None:
                    print("removing old station")
                    LFUtils.removePort(self.resource, self.sta_name, self.lfclient_url)
                    LFUtils.waitUntilPortsDisappear(self.resource, self.lfclient_url, [self.sta_name])

        # Create stations and turn dhcp on

        flags = 0x10000
        if self.dut_security == WPA2:
            flags += 0x400
        elif self.dut_security == OPEN:
            pass

        add_sta_data = {
            "shelf": 1,
            "resource": self.resource,
            "radio": self.radio,
            "ssid": self.dut_ssid,
            "key": self.dut_passwd,
            "mode": self.sta_mode,
            "mac": "xx:xx:xx:xx:*:xx",
            "flags": flags  # verbose, wpa2
        }
        for sta_name in self.station_names:
            add_sta_data["sta_name"] = sta_name;
            print("Adding new station %s " % self.sta_name)
            self.json_post("/cli-json/add_sta", add_sta_data)

        set_port_data = {
            "shelf": 1,
            "resource": self.resource,
            "current_flags": 0x80000000,  # use DHCP, not down
            "interest": 0x4002  # set dhcp, current flags
        }
        for sta_name in self.station_names:
            set_port_data["port"] = sta_name
            print("Configuring %s..." % sta_name)
            self.json_post("/cli-json/set_port", set_port_data)

        data = {"shelf": 1,
                "resource": self.resource,
                "port": "ALL",
                "probe_flags": 1}
        self.json_post("/cli-json/nc_show_ports", data)
        LFUtils.waitUntilPortsAdminUp(self.resource, self.lfclient_url, self.station_names)

        # station_info = self.jsonGet(self.mgr_url, "%s?fields=port,ip,ap" % (self.getStaUrl()))
        duration = 0
        maxTime = 300
        ip = "0.0.0.0"
        ap = ""
        print("Waiting for %s stations to associate to AP [%s]..." % (len(self.station_names), ap))

        connected_stations = []
        while (len(connected_stations) < len(self.station_names)) and (duration < maxTime):
            duration += 2
            time.sleep(2)
            for sta_name in self.station_names:
                sta_url = self.get_station_urls(sta_name)
                station_info = self.json_get(sta_url + "?fields=port,ip,ap")

                # LFUtils.debug_printer.pprint(station_info)
                if (station_info is not None) and ("interface" in station_info):
                    if "ip" in station_info["interface"]:
                        ip = station_info["interface"]["ip"]
                    if "ap" in station_info["interface"]:
                        ap = station_info["interface"]["ap"]

                if (ap == "Not-Associated") or (ap == ""):
                    if self.debugOn:
                        print("Waiting for %s associate to AP [%s]..." % (self.sta_name, ap))
                else:
                    if ip == "0.0.0.0":
                        if self.debugOn:
                            print("Waiting for %s to gain IP ..." % self.sta_name)
                    else:
                        connected_stations.append(sta_url)

        for sta_name in self.station_names:
            sta_url = self.get_station_url(sta_name)
            station_info = self.json_get(sta_url + "?fields=port,ip,ap")
            ap = station_info["interface"]["ap"]
            ip = station_info["interface"]["ip"]
            if (ap != "") and (ap != "Not-Associated"):
                print("Connected to AP: "+ap)
                if self.dut_bssid != "":
                    if self.dut_bssid.lower() == ap.lower():
                        self._pass(sta_name+" connected to BSSID: " + ap)
                        # self.test_results.append("PASSED: )
                        # print("PASSED: Connected to BSSID: "+ap)
                    else:
                        self._fail(sta_name+" connected to wrong BSSID, requested: %s  Actual: %s" % (self.dut_bssid, ap))
            else:
                self._fail(sta_name+" did not connect to AP")
                return False

            if ip == "0.0.0.0":
                self._fail("%s did not get an ip. Ending test" % sta_name)
            else:
                self._pass("%s connected to AP: %s  With IP: %s" % (sta_name, ap, ip))

        if self.passes() == False:
            print("Cleaning up...")
            self.remove_stations()
            return False

        # create endpoints and cxs
        # Create UDP endpoints
        cx_names = {}

        for sta_name in self.station_names:
            cx_names["testUDP-"+sta_name] = { "a": "testUDP-%s-A" % sta_name,
                                            "b": "testUDP-%s-B" % sta_name}
            data = {
                "alias": "testUDP-%s-A" % sta_name,
                "shelf": 1,
                "resource": self.resource,
                "port": sta_name,
                "type": "lf_udp",
                "ip_port": "-1",
                "min_rate": 1000000
            }
            self.json_post("/cli-json/add_endp", data)

            data = {
                "alias": "testUDP-%s-B" % sta_name,
                "shelf": 1,
                "resource": self.upstream_resource,
                "port": self.upstream_port,
                "type": "lf_udp",
                "ip_port": "-1",
                "min_rate": 1000000
            }
            self.json_post("/cli-json/add_endp", data)

            # Create CX
            data = {
                "alias": "testUDP-%" % sta_name,
                "test_mgr": "default_tm",
                "tx_endp": "testUDP-%s-A" % sta_name,
                "rx_endp": "testUDP-%s-B" % sta_name,
            }
            self.json_post("/cli-json/add_cx", data)

            # Create TCP endpoints
            cx_names["testTCP-"+sta_name] = { "a": "testUDP-%s-A" % sta_name,
                                            "b": "testUDP-%s-B" % sta_name}
            data = {
                "alias": "testTCP-%s-A" % sta_name,
                "shelf": 1,
                "resource": self.resource,
                "port": sta_name,
                "type": "lf_tcp",
                "ip_port": "0",
                "min_rate": 1000000
            }
            self.json_post("/cli-json/add_endp", data)

            data = {
                "alias": "testTCP-%s-B" % sta_name,
                "shelf": 1,
                "resource": self.upstream_resource,
                "port": self.upstream_port,
                "type": "lf_tcp",
                "ip_port": "-1",
                "min_rate": 1000000
            }
            self.json_post("/cli-json/add_endp", data)

            # Create CX
            data = {
                "alias": "testTCP-%s" % sta_name,
                "test_mgr": "default_tm",
                "tx_endp": "testTCP-A" % sta_name,
                "rx_endp": "testTCP-B" % sta_name,
            }
            self.json_post("/cli-json/add_cx", data)

            #cxNames = ["testTCP", "testUDP"]
            #endpNames = ["testTCP-A", "testTCP-B", "testUDP-A", "testUDP-B"]

        # start cx traffic
        print("\nStarting CX Traffic")
        for cx_name in cx_names.keys():
            data = {
                "test_mgr": "ALL",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }
            self.json_post("/cli-json/set_cx_state", data)

        # Refresh stats

        print("Refresh CX stats")
        for cx_name in cx_names.keys():
            data = {
                "test_mgr": "ALL",
                "cross_connect": cx_name
            }
            self.json_post("/cli-json/show_cxe", data)

        time.sleep(15)

        # stop cx traffic
        print("Stopping CX Traffic")
        for cx_name in cx_names.keys():
            data = {
                "test_mgr": "ALL",
                "cx_name": cx_name,
                "cx_state": "STOPPED"
            }
            self.json_post("/cli-json/set_cx_state", data)

        # Refresh stats
        print("\nRefresh CX stats")
        for cx_name in cx_names.keys():
            data = {
                "test_mgr": "ALL",
                "cross_connect": cx_name
            }
            self.json_post("/cli-json/show_cxe", data)

        # print("Sleeping for 5 seconds")
        time.sleep(5)

        # get data for endpoints JSON
        print("Collecting Data")
        for cx_name in cx_names.keys():

            try:
                ptest = self.json_get("/endp/%s?fields=tx+bytes,rx+bytes" % cx_names[cx_name]["a"])
                ptest_a_tx = ptest['endpoint']['tx bytes']
                ptest_a_rx = ptest['endpoint']['rx bytes']

                ptest = self.json_get("/endp/%s?fields=tx+bytes,rx+bytes" % cx_names[cx_name]["b"])
                ptest_b_tx = ptest['endpoint']['tx bytes']
                ptest_b_rx = ptest['endpoint']['rx bytes']

                self.compareVals("testTCP-A TX", ptest_a_tx)
                self.compareVals("testTCP-A RX", ptest_a_rx)

                self.compareVals("testTCP-B TX", ptest_b_tx)
                self.compareVals("testTCP-B RX", ptest_b_rx)

            except Exception as e:
                self.error(e)

        # print("\n")
        # self.test_results.append("Neutral message will fail")
        # self.test_results.append("FAILED message will fail")

        # print("\n")

        # remove all endpoints and cxs
        LFUtils.removePort(self.resource, self.sta_name, self.lfclient_url)
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
./sta_connect.py --dest 192.168.100.209 --dut_ssid OpenWrt-2 --dut_bssid 24:F5:A2:08:21:6C
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

    staConnect = StaConnect(lfjson_host, lfjson_port)

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

    staConnect.run()
    run_results = staConnect.get_result_list()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
    main()
