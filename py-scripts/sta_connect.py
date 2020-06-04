#!/usr/bin/env python3

#  This will create a station, create TCP and UDP traffic, run it a short amount of time,
#  and verify whether traffic was sent and received.  It also verifies the station connected
#  to the requested BSSID if bssid is specified as an argument.
#  The script will clean up the station and connections at the end of the test.

import sys
import argparse

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

# from LANforge import LFRequest
from LANforge import LFUtils
# from LANforge import LFCliBase
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from pprint import pprint

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


class StaConnect(LFCliBase):
    def __init__(self, host, port, _dut_ssid="MyAP", _dut_passwd="NA", _dut_bssid="",
                 _user="", _passwd="", _sta_mode="0", _radio="wiphy0",
                 _resource=1, _upstream_resource=1, _upstream_port="eth2",
                 _sta_name="sta001", _debugOn=False):
        # do not use `super(LFCLiBase,self).__init__(self, host, port, _debugOn)
        # that is py2 era syntax and will force self into the host variable, making you
        # very confused.
        super().__init__(host, port, _debugOn)

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
        self.sta_name = _sta_name
        self.sta_url = None  # defer construction
        self.upstream_url = None  # defer construction

    def getStaUrl(self):
        if self.sta_url is None:
            self.sta_url = f"port/1/{self.resource}/{self.sta_name}"
        return self.sta_url

    def getUpstreamUrl(self):
        if self.upstream_url is None:
            self.upstream_url = f"port/1/{self.upstream_resource}/{self.upstream_port}"
        return self.upstream_url

    # Compare pre-test values to post-test values
    # TODO: make this method add a results to an array
    # the calling client should collect results from that array
    @staticmethod
    def compareVals(name, postVal, results=None):
        # print(f"Comparing {name}")
        if postVal > 0:
            print("PASSED: %s %s" % (name, postVal))
            if results is not None:
               results.append("PASSED: %s %s" % (name, postVal))
        else:
            print("FAILED: %s did not report traffic: %s" % (name, postVal))
            if results is not None:
               results.append("FAILED: %s did not report traffic: %s" % (name, postVal))

    def run(self):
        self.check_connect()
        eth1IP = self.json_get(self.getUpstreamUrl())
        if eth1IP is None:
            print("Unable to query "+self.upstream_port+", bye")
            sys.exit(1)
        if eth1IP['interface']['ip'] == "0.0.0.0":
            print(f"Warning: {self.getUpstreamUrl()} lacks ip address")

        url = self.getStaUrl()
        response = super().json_get(url)
        if response is not None:
            if response["interface"] is not None:
                print("removing old station")
                LFUtils.removePort(self.resource, self.sta_name, self.mgr_url)
                LFUtils.waitUntilPortsDisappear(self.resource, self.mgr_url, [self.sta_name])

        # Create stations and turn dhcp on
        print("Creating station %s and turning on dhcp..." % self.sta_name)
        url = "cli-json/add_sta"
        flags = 0x10000
        if "" != self.dut_passwd:
            flags += 0x400
        data = {
            "shelf": 1,
            "resource": self.resource,
            "radio": self.radio,
            "sta_name": self.sta_name,
            "ssid": self.dut_ssid,
            "key": self.dut_passwd,
            "mode": self.sta_mode,
            "mac": "xx:xx:xx:xx:*:xx",
            "flags": flags  # verbose, wpa2
        }
        print("Adding new station %s " % self.sta_name)
        super().json_post(url, data)

        reqURL = "cli-json/set_port"
        data = {
            "shelf": 1,
            "resource": self.resource,
            "port": self.sta_name,
            "current_flags": 0x80000000,  # use DHCP, not down
            "interest": 0x4002  # set dhcp, current flags
        }
        print("Configuring %s..." % self.sta_name)
        super().json_post(reqURL, data)

        reqURL = "cli-json/nc_show_ports"
        data = {"shelf": 1,
                "resource": self.resource,
                "port": self.sta_name,
                "probe_flags": 1}
        super().json_post(reqURL, data)
        LFUtils.waitUntilPortsAdminUp(self.resource, self.mgr_url, [self.sta_name])

        # station_info = self.jsonGet(self.mgr_url, "%s?fields=port,ip,ap" % (self.getStaUrl()))
        duration = 0
        maxTime = 300
        ip = "0.0.0.0"
        ap = ""
        while (ip == "0.0.0.0") and (duration < maxTime):
            duration += 2
            time.sleep(2)
            station_info = super().json_get(f"{self.getStaUrl()}?fields=port,ip,ap")

            # LFUtils.debug_printer.pprint(station_info)
            if (station_info is not None) and ("interface" in station_info):
                if "ip" in station_info["interface"]:
                    ip = station_info["interface"]["ip"]
                if "ap" in station_info["interface"]:
                    ap = station_info["interface"]["ap"]

            if (ap == "Not-Associated") or (ap == ""):
                print("Waiting for %s associate to AP [%s]..." % (self.sta_name, ap))
            else:
                if ip == "0.0.0.0":
                    print("Waiting for %s to gain IP ..." % self.sta_name)

        if (ap != "") and (ap != "Not-Associated"):
            print(f"Connected to AP: {ap}")
            if self.dut_bssid != "":
                if self.dut_bssid.lower() == ap.lower():
                    print(f"PASSED: Connected to BSSID: {ap}")
                else:
                    print("FAILED: Connected to wrong BSSID, requested: %s  Actual: %s" % (self.dut_bssid, ap))
        else:
            print("FAILED:  Did not connect to AP")
            sys.exit(3)

        if ip == "0.0.0.0":
            print(f"FAILED: {self.sta_name} did not get an ip. Ending test")
            print("Cleaning up...")
            removePort(self.resource, self.sta_name, self.mgr_url)
            sys.exit(1)
        else:
            print("PASSED: Connected to AP: %s  With IP: %s" % (ap, ip))

        # create endpoints and cxs
        # Create UDP endpoints
        reqURL = "cli-json/add_endp"
        data = {
            "alias": "testUDP-A",
            "shelf": 1,
            "resource": self.resource,
            "port": self.sta_name,
            "type": "lf_udp",
            "ip_port": "-1",
            "min_rate": 1000000
        }
        super().json_post(reqURL, data)

        reqURL = "cli-json/add_endp"
        data = {
            "alias": "testUDP-B",
            "shelf": 1,
            "resource": self.upstream_resource,
            "port": self.upstream_port,
            "type": "lf_udp",
            "ip_port": "-1",
            "min_rate": 1000000
        }
        super().json_post(reqURL, data)

        # Create CX
        reqURL = "cli-json/add_cx"
        data = {
            "alias": "testUDP",
            "test_mgr": "default_tm",
            "tx_endp": "testUDP-A",
            "rx_endp": "testUDP-B",
        }
        super().json_post(reqURL, data)

        # Create TCP endpoints
        reqURL = "cli-json/add_endp"
        data = {
            "alias": "testTCP-A",
            "shelf": 1,
            "resource": self.resource,
            "port": self.sta_name,
            "type": "lf_tcp",
            "ip_port": "0",
            "min_rate": 1000000
        }
        super().json_post(reqURL, data)

        reqURL = "cli-json/add_endp"
        data = {
            "alias": "testTCP-B",
            "shelf": 1,
            "resource": self.upstream_resource,
            "port": self.upstream_port,
            "type": "lf_tcp",
            "ip_port": "-1",
            "min_rate": 1000000
        }
        super().json_post(reqURL, data)

        # Create CX
        reqURL = "cli-json/add_cx"
        data = {
            "alias": "testTCP",
            "test_mgr": "default_tm",
            "tx_endp": "testTCP-A",
            "rx_endp": "testTCP-B",
        }
        super().json_post(reqURL, data)

        cxNames = ["testTCP", "testUDP"]
        endpNames = ["testTCP-A", "testTCP-B",
                     "testUDP-A", "testUDP-B"]

        # start cx traffic
        print("\nStarting CX Traffic")
        for name in range(len(cxNames)):
            reqURL = "cli-json/set_cx_state"
            data = {
                "test_mgr": "ALL",
                "cx_name": cxNames[name],
                "cx_state": "RUNNING"
            }
            super().json_post(reqURL, data)

        # Refresh stats
        print("\nRefresh CX stats")
        for name in range(len(cxNames)):
            reqURL = "cli-json/show_cxe"
            data = {
                "test_mgr": "ALL",
                "cross_connect": cxNames[name]
            }
            super().json_post(reqURL, data)

        # print("Sleeping for 15 seconds")
        time.sleep(15)

        # stop cx traffic
        print("\nStopping CX Traffic")
        for name in range(len(cxNames)):
            reqURL = "cli-json/set_cx_state"
            data = {
                "test_mgr": "ALL",
                "cx_name": cxNames[name],
                "cx_state": "STOPPED"
            }
            super().json_post(reqURL, data)

        # Refresh stats
        print("\nRefresh CX stats")
        for name in range(len(cxNames)):
            reqURL = "cli-json/show_cxe"
            data = {
                "test_mgr": "ALL",
                "cross_connect": cxNames[name]
            }
            super().json_post(reqURL, data)

        # print("Sleeping for 5 seconds")
        time.sleep(5)

        # get data for endpoints JSON
        print("Collecting Data")
        try:
            ptestTCPA = super().json_get("endp/testTCP-A?fields=tx+bytes,rx+bytes")
            ptestTCPATX = ptestTCPA['endpoint']['tx bytes']
            ptestTCPARX = ptestTCPA['endpoint']['rx bytes']

            ptestTCPB = super().json_get("endp/testTCP-B?fields=tx+bytes,rx+bytes")
            ptestTCPBTX = ptestTCPB['endpoint']['tx bytes']
            ptestTCPBRX = ptestTCPB['endpoint']['rx bytes']

            ptestUDPA = super().json_get("endp/testUDP-A?fields=tx+bytes,rx+bytes")
            ptestUDPATX = ptestUDPA['endpoint']['tx bytes']
            ptestUDPARX = ptestUDPA['endpoint']['rx bytes']

            ptestUDPB = super().json_get("endp/testUDP-B?fields=tx+bytes,rx+bytes")
            ptestUDPBTX = ptestUDPB['endpoint']['tx bytes']
            ptestUDPBRX = ptestUDPB['endpoint']['rx bytes']
        except Exception as e:
            print("Something went wrong")
            print(e)
            print("Cleaning up...")
            reqURL = "cli-json/rm_vlan"
            data = {
                "shelf": 1,
                "resource": self.resource,
                "port": self.sta_name
            }

            self.json_post(reqURL, data)

            removeCX(self.mgr_url, cxNames)
            removeEndps(self.mgr_url, endpNames)
            sys.exit(1)

        print("\n")
        self.test_results = []
        self.compareVals("testTCP-A TX", ptestTCPATX, self.test_results)
        self.compareVals("testTCP-A RX", ptestTCPARX, self.test_results)

        self.compareVals("testTCP-B TX", ptestTCPBTX, self.test_results)
        self.compareVals("testTCP-B RX", ptestTCPBRX, self.test_results)

        self.compareVals("testUDP-A TX", ptestUDPATX, self.test_results)
        self.compareVals("testUDP-A RX", ptestUDPARX, self.test_results)

        self.compareVals("testUDP-B TX", ptestUDPBTX, self.test_results)
        self.compareVals("testUDP-B RX", ptestUDPBRX, self.test_results)
        print("\n")

        # remove all endpoints and cxs
        LFUtils.removePort(self.resource, self.sta_name, self.mgr_url)

        removeCX(self.mgr_url, cxNames)
        removeEndps(self.mgr_url, endpNames)

    def get_result_list(self):
        return self.test_results

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
