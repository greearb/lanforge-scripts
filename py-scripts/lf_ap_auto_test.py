#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

This script is used to automate running AP-Auto tests.  You
may need to view an AP Auto test configured through the GUI to understand
the options and how best to input data.
    
    ./lf_ap_auto_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name ap-auto-instance --config_name test_con --upstream 1.1.eth2 \
      --dut5_0 'linksys-8450 Default-SSID-5gl c4:41:1e:f5:3f:25 (2)' \
      --dut2_0 'linksys-8450 Default-SSID-2g c4:41:1e:f5:3f:24 (1)' \
      --max_stations_2 100 --max_stations_5 100 --max_stations_dual 200 \
      --radio2 1.1.wiphy0 --radio2 1.1.wiphy2 \
      --radio5 1.1.wiphy1 --radio5 1.1.wiphy3 --radio5 1.1.wiphy4 \
      --radio5 1.1.wiphy5 --radio5 1.1.wiphy6 --radio5 1.1.wiphy7 \
      --set 'Basic Client Connectivity' 1 --set 'Multi Band Performance' 1 \
      --set 'Skip 2.4Ghz Tests' 1 --set 'Skip 5Ghz Tests' 1 \
      --set 'Throughput vs Pkt Size' 0 --set 'Capacity' 0 --set 'Stability' 0 --set 'Band-Steering' 0 \
      --set 'Multi-Station Throughput vs Pkt Size' 0 --set 'Long-Term' 0

Note:
    --enable [option] will attempt to select any checkbox of that name to true.
    --disable [option] will attempt to un-select any checkbox of that name to true.
    --line_raw 'line contents' will add any setting to the test config.  This is
        useful way to support any options not specifically enabled by the
        command options.
    --set modifications will be applied after the other config has happened,
        so it can be used to override any other config.

Example of raw text config for ap-auto, to show other possible options:

sel_port-0: 1.1.sta00500
show_events: 1
show_log: 0
port_sorting: 0
kpi_id: AP Auto
bg: 0xE0ECF8
test_rig: Ferndale-01-Basic
show_scan: 1
auto_helper: 1
skip_2: 1
skip_5: 1
skip_5b: 1
skip_dual: 0
skip_tri: 1
dut5b-0: NA
dut5-0: linksys-8450 Default-SSID-5gl c4:41:1e:f5:3f:25 (2)
dut2-0: linksys-8450 Default-SSID-2g c4:41:1e:f5:3f:24 (1)
dut5b-1: NA
dut5-1: NA
dut2-1: NA
dut5b-2: NA
dut5-2: NA
dut2-2: NA
spatial_streams: AUTO
bandw_options: AUTO
modes: Auto
upstream_port: 1.1.2 eth2
operator: 
mconn: 1
tos: 0
vid_buf: 1000000
vid_speed: 700000
reset_stall_thresh_udp_dl: 9600
cx_prcnt: 950000
cx_open_thresh: 35
cx_psk_thresh: 75
cx_1x_thresh: 130
reset_stall_thresh_udp_ul: 9600
reset_stall_thresh_tcp_dl: 9600
reset_stall_thresh_tcp_ul: 9600
reset_stall_thresh_l4: 100000
reset_stall_thresh_voip: 20000
stab_mcast_dl_min: 100000
stab_mcast_dl_max: 0
stab_udp_dl_min: 56000
stab_udp_dl_max: 0
stab_udp_ul_min: 56000
stab_udp_ul_max: 0
stab_tcp_dl_min: 500000
stab_tcp_dl_max: 0
stab_tcp_ul_min: 500000
stab_tcp_ul_max: 0
dl_speed: 85%
ul_speed: 85%
max_stations_2: 100
max_stations_5: 100
max_stations_5b: 64
max_stations_dual: 200
max_stations_tri: 64
lt_sta: 2
voip_calls: 0
lt_dur: 3600
reset_dur: 600
lt_gi: 30
dur20: 20
hunt_retries: 1
hunt_iter: 15
bind_bssid: 1
set_txpower_default: 0
cap_dl: 1
cap_ul: 0
cap_use_pkt_sizes: 0
stability_reset_radios: 0
stability_use_pkt_sizes: 0
pkt_loss_thresh: 10000
frame_sizes: 200, 512, 1024, MTU
capacities: 1, 2, 5, 10, 20, 40, 64, 128, 256, 512, 1024, MAX
pf_text0: 2.4 DL 200 70Mbps
pf_text1: 2.4 DL 512 110Mbps
pf_text2: 2.4 DL 1024 115Mbps
pf_text3: 2.4 DL MTU 120Mbps
pf_text4: 
pf_text5: 2.4 UL 200 88Mbps
pf_text6: 2.4 UL 512 106Mbps
pf_text7: 2.4 UL 1024 115Mbps
pf_text8: 2.4 UL MTU 120Mbps
pf_text9: 
pf_text10: 5 DL 200 72Mbps
pf_text11: 5 DL 512 185Mbps
pf_text12: 5 DL 1024 370Mbps
pf_text13: 5 DL MTU 525Mbps
pf_text14: 
pf_text15: 5 UL 200 90Mbps
pf_text16: 5 UL 512 230Mbps
pf_text17: 5 UL 1024 450Mbps
pf_text18: 5 UL MTU 630Mbps
radio2-0: 1.1.4 wiphy0
radio2-1: 1.1.6 wiphy2
radio5-0: 1.1.5 wiphy1
radio5-1: 1.1.7 wiphy3
radio5-2: 1.1.8 wiphy4
radio5-3: 1.1.9 wiphy5
radio5-4: 1.1.10 wiphy6
radio5-5: 1.1.11 wiphy7
basic_cx: 0
tput: 0
tput_multi: 0
tput_multi_tcp: 1
tput_multi_udp: 1
tput_multi_dl: 1
tput_multi_ul: 1
dual_band_tput: 1
capacity: 0
band_steering: 0
longterm: 0
mix_stability: 0
loop_iter: 1
reset_batch_size: 1
reset_duration_min: 10000
reset_duration_max: 60000
bandsteer_always_5g: 0

"""

import sys
import os
import argparse
import time
import json
from os import path

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_test_manager import cv_test as cvtest
from cv_commands import chamberview as cv
from cv_test_reports import lanforge_reports as lf_rpt


class ApAutoTest(cvtest):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="ap_auto_instance",
                 config_name="ap_auto_config",
                 upstream="1.1.eth1",
                 pull_report=False,
                 dut5_0="NA",
                 dut2_0="NA",
                 load_old_cfg=False,
                 max_stations_2=100,
                 max_stations_5=100,
                 max_stations_dual=200,
                 radio2=[],
                 radio5=[],
                 enables=[],
                 disables=[],
                 raw_lines=[],
                 sets=[],
                 ):
        super().__init__(lfclient_host=lf_host, lfclient_port=lf_port)

        self.lf_host = lf_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password =lf_password
        self.createCV = cv(lf_host, lf_port);
        self.instance_name = instance_name
        self.config_name = config_name
        self.upstream = upstream
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "AP-Auto"
        self.dut5_0 = dut5_0
        self.dut2_0 = dut2_0
        self.max_stations_2 = max_stations_2
        self.max_stations_5 = max_stations_5
        self.max_stations_dual = max_stations_dual
        self.radio2 = radio2
        self.radio5 = radio5
        self.enables = enables
        self.disables = disables
        self.raw_lines = raw_lines
        self.sets = sets

    def setup(self):
        # Nothing to do at this time.
        return


    def run(self):
        self.createCV.sync_cv()
        time.sleep(2)
        self.createCV.sync_cv()

        blob_test = "%s-"%(self.test_name)

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = ["upstream_port: " + self.upstream,
                       "dut5-0: " + self.dut5_0,
                       "dut2-0: " + self.dut2_0,
                       "max_stations_2: " + str(self.max_stations_2),
                       "max_stations_5: " + str(self.max_stations_5),
                       "max_stations_dual: " + str(self.max_stations_dual),
                       ]

        ridx = 0
        for r in self.radio2:
            cfg_options.append("radio2-%i: %s"%(ridx, r[0]))
            ridx += 1

        ridx = 0
        for r in self.radio5:
            cfg_options.append("radio5-%i: %s"%(ridx, r[0]))
            ridx += 1

        for en in self.enables:
            cfg_options.append("%s: 1"%(en[0]))

        for en in self.disables:
            cfg_options.append("%s: 0"%(en[0]))

        for r in self.raw_lines:
            cfg_options.append(r[0])

        # We deleted the scenario earlier, now re-build new one line at a time.
        for value in cfg_options:
            self.create_test_config(self.config_name, blob_test, value)

        # Request GUI update its text blob listing.
        self.show_text_blob(self.config_name, blob_test, False)

        # Hack, not certain if the above show returns before the action has been completed
        # or not, so we sleep here until we have better idea how to query if GUI knows about
        # the text blob.
        time.sleep(5)

        load_old = "false"
        if self.load_old_cfg:
            load_old = "true"

        for i in range(60):
            response = self.create_test(self.test_name, self.instance_name, load_old)
            d1 = {k: v for e in response for (k, v) in e.items()}
            if d1["LAST"]["response"] == "OK":
                break
            else:
                time.sleep(1)

        self.load_test_config(self.config_name, self.instance_name)
        self.auto_save_report(self.instance_name)

        # Apply 'sets'
        for kv in self.sets:
            cmd = "cv set '%s' '%s' '%s'" % (self.instance_name, kv[0], kv[1])
            print("Running CV command: ", cmd)
            self.run_cv_cmd(cmd)

        response = self.start_test(self.instance_name)
        d1 = {k: v for e in response for (k, v) in e.items()}
        if d1["LAST"]["response"].__contains__("Could not find instance:"):
            print("ERROR:  start_test failed: ", d1["LAST"]["response"], "\n");
            # pprint(response)
            exit(1)

        while (True):
            check = self.get_report_location(self.instance_name)
            location = json.dumps(check[0]["LAST"]["response"])
            if location != "\"Report Location:::\"":
                location = location.replace("Report Location:::", "")
                self.close_instance(self.instance_name)
                self.cancel_instance(self.instance_name)
                location = location.strip("\"")
                report = lf_rpt()
                print(location)
                try:
                    if self.pull_report:
                        report.pull_reports(hostname=self.lf_host, username=self.lf_user, password=self.lf_password,
                                            report_location=location)
                except:
                    raise Exception("Could not find Reports")
                break
            time.sleep(1)

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name


def main():

    parser = argparse.ArgumentParser("""
    Open this file in an editor and read the top notes for more details.
    
    Example:
    ./lf_ap_auto_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name ap-auto-instance --config_name test_con --upstream 1.1.eth2 \
      --dut5_0 'linksys-8450 Default-SSID-5gl c4:41:1e:f5:3f:25 (2)' \
      --dut2_0 'linksys-8450 Default-SSID-2g c4:41:1e:f5:3f:24 (1)' \
      --max_stations_2 100 --max_stations_5 100 --max_stations_dual 200 \
      --radio2 1.1.wiphy0 --radio2 1.1.wiphy2 \
      --radio5 1.1.wiphy1 --radio5 1.1.wiphy3 --radio5 1.1.wiphy4 \
      --radio5 1.1.wiphy5 --radio5 1.1.wiphy6 --radio5 1.1.wiphy7 \
      --set 'Basic Client Connectivity' 1 --set 'Multi Band Performance' 1 \
      --set 'Skip 2.4Ghz Tests' 1 --set 'Skip 5Ghz Tests' 1 \
      --set 'Throughput vs Pkt Size' 0 --set 'Capacity' 0 --set 'Stability' 0 --set 'Band-Steering' 0 \
      --set 'Multi-Station Throughput vs Pkt Size' 0 --set 'Long-Term' 0
      """
                                     )

    parser.add_argument("-m", "--mgr", type=str, default="localhost",
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_user", type=str, default="lanforge",
                        help="LANforge username to pull reports")
    parser.add_argument("--lf_password", type=str, default="lanforge",
                        help="LANforge Password to pull reports")
    parser.add_argument("-i", "--instance_name", type=str,
                        help="create test instance")
    parser.add_argument("-c", "--config_name", type=str,
                        help="Config file name")
    parser.add_argument("-u", "--upstream", type=str, default="1.1.eth1",
                        help="Upstream port for wifi capacity test ex. 1.1.eth1")
    parser.add_argument("-r", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")
    parser.add_argument("--load_old_cfg", default=False, action='store_true',
                        help="Should we first load defaults from previous run of the capacity test?  Default is False")

    parser.add_argument("--max_stations_2", type=int, default=100,
                        help="Specify maximum 2.4Ghz stations")
    parser.add_argument("--max_stations_5", type=int, default=100,
                        help="Specify maximum 5Ghz stations")
    parser.add_argument("--max_stations_dual", type=int, default=200,
                        help="Specify maximum stations for dual-band tests")
    parser.add_argument("--dut5_0", type=str, default="NA",
                        help="Specify 5Ghz DUT entry.  Syntax is somewhat tricky:  DUT-name SSID BSID (bssid-idx), example: linksys-8450 Default-SSID-5gl c4:41:1e:f5:3f:25 (2)")
    parser.add_argument("--dut2_0", type=str, default="NA",
                        help="Specify 5Ghz DUT entry.  Syntax is somewhat tricky:  DUT-name SSID BSID (bssid-idx), example: linksys-8450 Default-SSID-2g c4:41:1e:f5:3f:24 (1)")

    parser.add_argument("--radio2", action='append', nargs=1, default=[],
                        help="Specify 2.4Ghz radio.  May be specified multiple times.")
    parser.add_argument("--radio5", action='append', nargs=1, default=[],
                        help="Specify 5Ghz radio.  May be specified multiple times.")
    parser.add_argument("--enable", action='append', nargs=1, default=[],
                        help="Specify options to enable (set value to 1).  Example: --enable basic_cx   See example raw text config for possible options.  May be specified multiple times.  Most tests are enabled by default, except: longterm")
    parser.add_argument("--disable", action='append', nargs=1, default=[],
                        help="Specify options to disable (set value to 0).  Example: --disable basic_cx   See example raw text config for possible options.  May be specified multiple times.  Most tests are enabled by default, so you probably want to disable most of them: basic_cx tput tput_multi dual_band_tput capacity band_steering mix_stability")
    parser.add_argument("--set", action='append', nargs=2, default=[],
                        help="Specify options to set values based on their label in the GUI. Example: --set 'Basic Client Connectivity' 1  May be specified multiple times.")
    parser.add_argument("--raw_line", action='append', nargs=1, default=[],
                        help="Specify lines of the raw config file.  Example: --raw_line 'test_rig: Ferndale-01-Basic'  See example raw text config for possible options.  This is catch-all for any options not available to be specified elsewhere.  May be specified multiple times.")    
    args = parser.parse_args()

    CV_Test = ApAutoTest(lf_host = args.mgr,
                         lf_port = args.port,
                         lf_user = args.lf_user,
                         lf_password = args.lf_password,
                         instance_name = args.instance_name,
                         config_name = args.config_name,
                         upstream = args.upstream,
                         pull_report = args.pull_report,
                         dut5_0 = args.dut5_0,
                         dut2_0 = args.dut2_0,
                         load_old_cfg = args.load_old_cfg,
                         max_stations_2 = args.max_stations_2,
                         max_stations_5 = args.max_stations_5,
                         max_stations_dual = args.max_stations_dual,
                         radio2 = args.radio2,
                         radio5 = args.radio5,
                         enables = args.enable,
                         disables = args.disable,
                         raw_lines = args.raw_line,
                         sets = args.set
                         )
    CV_Test.setup()
    CV_Test.run()


if __name__ == "__main__":
    main()
