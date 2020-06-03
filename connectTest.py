#!/usr/bin/env python3
import sys

if 'py-json' not in sys.path:
    sys.path.append('py-json')

from LANforge import LFUtils
from LANforge.LFUtils import *
from LANforge.lfcli_base import LFCliBase

import create_genlink as genl

debugOn = True
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

mgrURL = "http://localhost:8080/"
staName = "sta0"
staNameUri = "port/1/1/" + staName


class ConnectTest(LFCliBase):
    def __init__(self, lfhost, lfport):
        super().__init__(lfhost, lfport, True)
        super().checkConnect()

    # compare pre-test values to post-test values
    @staticmethod
    def CompareVals(_name, preVal, postVal):
        print(f"Comparing {_name}")
        if postVal > preVal:
            print("     Test Passed")
        else:
            print(f" Test Failed: {_name} did not increase after 5 seconds")

    def run(self):
        print("See home/lanforge/Documents/connectTestLogs/connectTestLatest for specific values on latest test")

        eth1IP = super().jsonGet("port/1/1/eth1")
        if eth1IP['interface']['ip'] == "0.0.0.0":
            print("Warning: Eth1 lacks ip address")
            exit(1)

        # Create stations and turn dhcp on
        print("Creating station and turning on dhcp")

        response = super().jsonGet(staNameUri)
        if response is not None:
            if response["interface"] is not None:
                print("removing old station")
                removePort(1, staName, mgrURL)
                waitUntilPortsDisappear(1, mgrURL, [staName])
                time.sleep(1)

        url = "cli-json/add_sta"
        data = {
            "shelf": 1,
            "resource": 1,
            "radio": "wiphy0",
            "sta_name": staName,
            "ssid": "jedway-wpa2-x2048-5-1",
            "key": "jedway-wpa2-x2048-5-1",
            "mode": 0,
            "mac": "xx:xx:xx:xx:*:xx",
            "flags": (0x400 + 0x20000 + 0x1000000000)  # create admin down
        }
        super().jsonPost(url, data)
        time.sleep(0.05)
        reqURL = "cli-json/set_port"
        data = {
            "shelf": 1,
            "resource": 1,
            "port": staName,
            "current_flags": (0x1 + 0x80000000),
            "interest": (0x2 + 0x4000 + 0x800000)  # current, dhcp, down,
        }
        super().jsonPost(reqURL, data)
        time.sleep(0.5)
        super().jsonPost("cli-json/set_port", portUpRequest(1, staName))

        reqURL = "cli-json/nc_show_ports"
        data = {"shelf": 1,
                "resource": 1,
                "port": staName,
                "probe_flags": 1}
        super().jsonPost(reqURL, data)
        time.sleep(0.5)
        waitUntilPortsAdminUp(1, mgrURL, [staName])

        duration = 0
        maxTime = 300
        ip = "0.0.0.0"
        while (ip == "0.0.0.0") and (duration < maxTime):
            station_info = super().jsonGet(staNameUri + "?fields=port,ip")
            LFUtils.debug_printer.pprint(station_info)
            if (station_info is not None) and ("interface" in station_info) and ("ip" in station_info["interface"]):
                ip = station_info["interface"]["ip"]
            if ip == "0.0.0.0":
                duration += 4
                time.sleep(4)
            else:
                break

        if duration >= maxTime:
            print(staName+" failed to get an ip. Ending test")
            print("Cleaning up...")
            removePort(1, staName, mgrURL)
            sys.exit(1)

        print("Creating endpoints and cross connects")
        # create cx for tcp and udp
        cmd = (
            f"./lf_firemod.pl --action create_cx --cx_name testTCP --use_ports {staName},eth1 --use_speeds  360000,150000 --endp_type tcp > /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        cmd = (
            f"./lf_firemod.pl --action create_cx --cx_name testUDP --use_ports {staName},eth1 --use_speeds  360000,150000 --endp_type udp >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        time.sleep(.05)

        # create l4 endpoint
        url = "cli-json/add_l4_endp"
        data = {
            "alias": "l4Test",
            "shelf": 1,
            "resource": 1,
            "port": "sta00000",
            "type": "l4_generic",
            "timeout": 1000,
            "url_rate": 600,
            "url": "dl http://10.40.0.1/ /dev/null"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create cx for l4_endp
        url = "cli-json/add_cx"
        data = {
            "alias": "CX_l4Test",
            "test_mgr": "default_tm",
            "tx_endp": "l4Test",
            "rx_endp": "NA"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create fileio endpoint
        url = "cli-json/add_file_endp"
        data = {
            "alias": "fioTest",
            "shelf": 1,
            "resource": 1,
            "port": "sta00000",
            "type": "fe_nfs",
            "directory": "/mnt/fe-test"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create fileio cx
        url = "cli-json/add_cx"
        data = {
            "alias": "CX_fioTest",
            "test_mgr": "default_tm",
            "tx_endp": "fioTest",
            "rx_endp": "NA"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create generic endpoints
        genl.createGenEndp("genTest1", 1, 1, "sta00000", "gen_generic")
        genl.createGenEndp("genTest2", 1, 1, "sta00000", "gen_generic")
        genl.setFlags("genTest1", "ClearPortOnStart", 1)
        genl.setFlags("genTest2", "ClearPortOnStart", 1)
        genl.setFlags("genTest2", "Unmanaged", 1)
        genl.setCmd("genTest1", "lfping  -i 0.1 -I sta00000 10.40.0.1")
        time.sleep(.05)

        # create generic cx
        url = "cli-json/add_cx"
        data = {
            "alias": "CX_genTest1",
            "test_mgr": "default_tm",
            "tx_endp": "genTest1",
            "rx_endp": "genTest2"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create redirects for wanlink
        url = "cli-json/add_rdd"
        data = {
            "shelf": 1,
            "resource": 1,
            "port": "rdd0",
            "peer_ifname": "rdd1"
        }
        super().jsonPost(url, data)

        url = "cli-json/add_rdd"
        data = {
            "shelf": 1,
            "resource": 1,
            "port": "rdd1",
            "peer_ifname": "rdd0"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # reset redirect ports
        url = "cli-json/reset_port"
        data = {
            "shelf": 1,
            "resource": 1,
            "port": "rdd0"
        }
        super().jsonPost(url, data)

        url = "cli-json/reset_port"
        data = {
            "shelf": 1,
            "resource": 1,
            "port": "rdd1"
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create wanlink endpoints
        url = "cli-json/add_wl_endp"
        data = {
            "alias": "wlTest1",
            "shelf": 1,
            "resource": 1,
            "port": "rdd0",
            "latency": 20,
            "max_rate": 1544000
        }
        super().jsonPost(url, data)

        url = "cli-json/add_wl_endp"
        data = {
            "alias": "wlTest2",
            "shelf": 1,
            "resource": 1,
            "port": "rdd1",
            "latency": 30,
            "max_rate": 1544000
        }
        super().jsonPost(url, data)
        time.sleep(.05)

        # create wanlink cx
        url = "cli-json/add_cx"
        data = {
            "alias": "CX_wlTest1",
            "test_mgr": "default_tm",
            "tx_endp": "wlTest1",
            "rx_endp": "wlTest2"
        }
        super().jsonPost(url, data)
        time.sleep(.5)

        cxNames = ["testTCP", "testUDP", "CX_l4Test", "CX_fioTest", "CX_genTest1", "CX_wlTest1"]

        # get data before running traffic
        try:
            testTCPA = super().jsonGet("endp/testTCP-A?fields=tx+bytes,rx+bytes")
            testTCPATX = testTCPA['endpoint']['tx bytes']
            testTCPARX = testTCPA['endpoint']['rx bytes']

            testTCPB = super().jsonGet("endp/testTCP-B?fields=tx+bytes,rx+bytes")
            testTCPBTX = testTCPB['endpoint']['tx bytes']
            testTCPBRX = testTCPB['endpoint']['rx bytes']

            testUDPA = super().jsonGet("endp/testUDP-A?fields=tx+bytes,rx+bytes")
            testUDPATX = testUDPA['endpoint']['tx bytes']
            testUDPARX = testUDPA['endpoint']['rx bytes']

            testUDPB = super().jsonGet("endp/testUDP-B?fields=tx+bytes,rx+bytes")
            testUDPBTX = testUDPB['endpoint']['tx bytes']
            testUDPBRX = testUDPB['endpoint']['rx bytes']

            l4Test = super().jsonGet("layer4/l4Test?fields=bytes-rd")
            l4TestBR = l4Test['endpoint']['bytes-rd']

            genTest1 = super().jsonGet("generic/genTest1?fields=last+results")
            genTest1LR = genTest1['endpoint']['last results']

            wlTest1 = super().jsonGet("wl_ep/wlTest1")
            wlTest1TXB = wlTest1['endpoint']['tx bytes']
            wlTest1RXP = wlTest1['endpoint']['rx pkts']
            wlTest2 = super().jsonGet("wl_ep/wlTest2")
            wlTest2TXB = wlTest2['endpoint']['tx bytes']
            wlTest2RXP = wlTest2['endpoint']['rx pkts']

        except Exception as e:
            print("Something went wrong")
            print(e)
            print("Cleaning up...")
            LFUtils.removePort(1, staName, mgrURL)
            endpNames = ["testTCP-A", "testTCP-B",
                         "testUDP-A", "testUDP-B",
                         "l4Test", "fioTest",
                         "genTest1", "genTest2",
                         "wlTest1", "wlTest2"]
            removeCX(mgrURL, cxNames)
            removeEndps(mgrURL, endpNames)
            sys.exit(1)

        # start cx traffic
        print("\nStarting CX Traffic")
        for name in range(len(cxNames)):
            cmd = (
                f"./lf_firemod.pl --mgr localhost --quiet yes --action do_cmd --cmd \"set_cx_state default_tm {cxNames[name]} RUNNING\" >> /tmp/connectTest.log")
            execWrap(cmd)

        # print("Sleeping for 5 seconds")
        time.sleep(5)

        # show tx and rx bytes for ports

        os.system("echo  eth1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_portmod.pl --quiet 1 --manager localhost --port_name eth1 --show_port \"Txb,Rxb\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  sta00000 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_portmod.pl --quiet 1 --manager localhost --port_name sta00000 --show_port \"Txb,Rxb\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)

        # show tx and rx for endpoints PERL
        os.system("echo  TestTCP-A >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name testTCP-A --endp_vals \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  TestTCP-B >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name testTCP-B --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  TestUDP-A >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name testUDP-A --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  TestUDP-B >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name testUDP-B --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  l4Test >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name l4Test --endp_vals Bytes-Read-Total >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  fioTest >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name fioTest --endp_vals \"Bytes Written,Bytes Read\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  genTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name genTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  wlTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name wlTest1 --endp_vals \"Rx Pkts,Tx Bytes,Cur-Backlog,Dump File,Tx3s\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)
        os.system("echo  wlTest2 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        cmd = (
            "./lf_firemod.pl --action show_endp --endp_name wlTest2 --endp_vals \"Rx Pkts,Tx Bytes,Cur-Backlog,Dump File,Tx3s\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
        execWrap(cmd)

        # stop cx traffic
        print("Stopping CX Traffic")
        for name in range(len(cxNames)):
            cmd = (
                f"./lf_firemod.pl --mgr localhost --quiet yes --action do_cmd --cmd \"set_cx_state default_tm {cxNames[name]} STOPPED\"  >> /tmp/connectTest.log")
            execWrap(cmd)
        # print("Sleeping for 15 seconds")
        time.sleep(15)

        # get data for endpoints JSON
        print("Collecting Data")
        try:
            ptestTCPA = super().jsonGet("endp/testTCP-A?fields=tx+bytes,rx+bytes")
            ptestTCPATX = ptestTCPA['endpoint']['tx bytes']
            ptestTCPARX = ptestTCPA['endpoint']['rx bytes']

            ptestTCPB = super().jsonGet("endp/testTCP-B?fields=tx+bytes,rx+bytes")
            ptestTCPBTX = ptestTCPB['endpoint']['tx bytes']
            ptestTCPBRX = ptestTCPB['endpoint']['rx bytes']

            ptestUDPA = super().jsonGet("endp/testUDP-A?fields=tx+bytes,rx+bytes")
            ptestUDPATX = ptestUDPA['endpoint']['tx bytes']
            ptestUDPARX = ptestUDPA['endpoint']['rx bytes']

            ptestUDPB = super().jsonGet("endp/testUDP-B?fields=tx+bytes,rx+bytes")
            ptestUDPBTX = ptestUDPB['endpoint']['tx bytes']
            ptestUDPBRX = ptestUDPB['endpoint']['rx bytes']

            pl4Test = super().jsonGet("layer4/l4Test?fields=bytes-rd")
            pl4TestBR = pl4Test['endpoint']['bytes-rd']

            pgenTest1 = super().jsonGet("generic/genTest1?fields=last+results")
            pgenTest1LR = pgenTest1['endpoint']['last results']

            pwlTest1 = super().jsonGet("wl_ep/wlTest1")
            pwlTest1TXB = pwlTest1['endpoint']['tx bytes']
            pwlTest1RXP = pwlTest1['endpoint']['rx pkts']
            pwlTest2 = super().jsonGet("wl_ep/wlTest2")
            pwlTest2TXB = pwlTest2['endpoint']['tx bytes']
            pwlTest2RXP = pwlTest2['endpoint']['rx pkts']
        except Exception as e:
            print("Something went wrong")
            print(e)
            print("Cleaning up...")
            reqURL = "cli-json/rm_vlan"
            data = {
                "shelf": 1,
                "resource": 1,
                "port": staName
            }
            super().jsonPost(reqURL, data)

            endpNames = ["testTCP-A", "testTCP-B",
                         "testUDP-A", "testUDP-B",
                         "l4Test", "fioTest",
                         "genTest1", "genTest2",
                         "wlTest1", "wlTest2"]
            removeCX(mgrURL, cxNames)
            removeEndps(mgrURL, endpNames)
            sys.exit(1)

        # print("Sleeping for 5 seconds")
        time.sleep(5)

        print("\n")
        self.CompareVals("testTCP-A TX", testTCPATX, ptestTCPATX)
        self.CompareVals("testTCP-A RX", testTCPARX, ptestTCPARX)
        self.CompareVals("testTCP-B TX", testTCPBTX, ptestTCPBTX)
        self.CompareVals("testTCP-B RX", testTCPBRX, ptestTCPBRX)
        self.CompareVals("testUDP-A TX", testUDPATX, ptestUDPATX)
        self.CompareVals("testUDP-A RX", testUDPARX, ptestUDPARX)
        self.CompareVals("testUDP-B TX", testUDPBTX, ptestUDPBTX)
        self.CompareVals("testUDP-B RX", testUDPBRX, ptestUDPBRX)
        self.CompareVals("l4Test Bytes Read", l4TestBR, pl4TestBR)
        self.CompareVals("genTest1 Last Results", genTest1LR, pgenTest1LR)
        self.CompareVals("wlTest1 TX Bytes", wlTest1TXB, pwlTest1TXB)
        self.CompareVals("wlTest1 RX Pkts", wlTest1RXP, pwlTest1RXP)
        self.CompareVals("wlTest2 TX Bytes", wlTest2TXB, pwlTest2TXB)
        self.CompareVals("wlTest2 RX Pkts", wlTest2RXP, pwlTest2RXP)
        print("\n")

        # remove all endpoints and cxs
        print("Cleaning up...")
        LFUtils.removePort(1, "sta00000", mgrURL)

        endpNames = ["testTCP-A", "testTCP-B",
                     "testUDP-A", "testUDP-B",
                     "l4Test", "fioTest",
                     "genTest1", "genTest2",
                     "wlTest1", "wlTest2"]
        removeCX(mgrURL, cxNames)
        removeEndps(mgrURL, endpNames)


# ~class

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    test = ConnectTest(lfjson_host, lfjson_port)
    test.run()


if __name__ == "__main__":
    main()
