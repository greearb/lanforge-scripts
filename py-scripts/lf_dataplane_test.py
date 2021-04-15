#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

This script is used to automate running Dataplane tests.  You
may need to view a Dataplane test configured through the GUI to understand
the options and how best to input data.
    
    ./lf_dataplane_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name dataplane-instance --config_name test_con --upstream 1.1.eth2 \
      --dut linksys-8450 --duration 15s --station 1.1.sta01500 \
      --download_speed 85% --upload_speed 0 \
      --raw_line 'pkts: Custom;60;142;256;512;1024;MTU' \
      --raw_line 'cust_pkt_sz: 88 1200' \
      --raw_line 'directions: DUT Transmit;DUT Receive' \
      --raw_line 'traffic_types: UDP;TCP'

Note:
    --raw_line 'line contents' will add any setting to the test config.  This is
        useful way to support any options not specifically enabled by the
        command options.
    --set modifications will be applied after the other config has happened,
        so it can be used to override any other config.

Example of raw text config for Dataplane, to show other possible options:

show_events: 1
show_log: 0
port_sorting: 0
kpi_id: Dataplane Pkt-Size
notes0: ec5211 in bridge mode, wpa2 auth.
bg: 0xE0ECF8
test_rig: 
show_scan: 1
auto_helper: 0
skip_2: 0
skip_5: 0
skip_5b: 1
skip_dual: 0
skip_tri: 1
selected_dut: ea8300
duration: 15000
traffic_port: 1.1.157 sta01500
upstream_port: 1.1.2 eth2
path_loss: 10
speed: 85%
speed2: 0Kbps
min_rssi_bound: -150
max_rssi_bound: 0
channels: AUTO
modes: Auto
pkts: Custom;60;142;256;512;1024;MTU
spatial_streams: AUTO
security_options: AUTO
bandw_options: AUTO
traffic_types: UDP;TCP
directions: DUT Transmit;DUT Receive
txo_preamble: OFDM
txo_mcs: 0 CCK, OFDM, HT, VHT
txo_retries: No Retry
txo_sgi: OFF
txo_txpower: 15
attenuator: 0
attenuator2: 0
attenuator_mod: 255
attenuator_mod2: 255
attenuations: 0..+50..950
attenuations2: 0..+50..950
chamber: 0
tt_deg: 0..+45..359
cust_pkt_sz: 88 1200
show_bar_labels: 1
show_prcnt_tput: 0
show_3s: 0
show_ll_graphs: 0
show_gp_graphs: 1
show_1m: 1
pause_iter: 0
outer_loop_atten: 0
show_realtime: 1
operator: 
mconn: 1
mpkt: 1000
tos: 0
loop_iterations: 1

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


class DataplaneTest(cvtest):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="dpt_instance",
                 config_name="dpt_config",
                 upstream="1.1.eth2",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_speed="0",
                 download_speed="85%",
                 duration="15s",
                 station="1.1.sta01500",
                 dut="NA",
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
        self.dut = dut
        self.duration = duration
        self.upstream = upstream
        self.station = station
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "Dataplane"
        self.upload_speed = upload_speed
        self.download_speed = download_speed
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

        blob_test = "dataplane-test-latest-"

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = ["upstream_port: " + self.upstream,
                       "traffic_port: " + self.station,
                       "speed: " + self.download_speed,
                       "speed2: " + self.upload_speed,
                       "duration: " + self.duration,
                       "selected_dut: " + self.dut,
                       ]

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
    parser.add_argument("-u", "--upstream", type=str, default="1.1.eth2",
                        help="Upstream port for wifi capacity test ex. 1.1.eth2")
    parser.add_argument("--station", type=str, default="1.1.sta01500",
                        help="Station to be used in this test, example: 1.1.sta01500")
    parser.add_argument("-r", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")
    parser.add_argument("--load_old_cfg", default=False, action='store_true',
                        help="Should we first load defaults from previous run of the capacity test?  Default is False")

    parser.add_argument("--dut", default="", required=True,
                        help="Specify DUT used by this test, example: linksys-8450")
    parser.add_argument("--download_speed", default="85%",
                        help="Specify requested download speed.  Percentage of theoretical is also supported.  Default: 85%")
    parser.add_argument("--upload_speed", default="0",
                        help="Specify requested upload speed.  Percentage of theoretical is also supported.  Default: 0")
    parser.add_argument("--duration", default="15s",
                        help="Specify duration of each traffic run")

    parser.add_argument("--enable", action='append', nargs=1, default=[],
                        help="Specify options to enable (set value to 1). Example:  --enable show_log  See example raw text config for possible options.  May be specified multiple times.")
    parser.add_argument("--disable", action='append', nargs=1, default=[],
                        help="Specify options to disable (set value to 0).  Example: --disable show_events   See example raw text config for possible options.  May be specified multiple times.")
    parser.add_argument("--set", action='append', nargs=2, default=[],
                        help="Specify options to set values based on their label in the GUI. Example: --set 'IP ToS:' 64  May be specified multiple times.")
    parser.add_argument("--raw_line", action='append', nargs=1, default=[],
                        help="Specify lines of the raw config file.  Example: --raw_line 'pkts: Custom;60;142;256;512;1024;MTU'  See example raw text config for possible options.  This is catch-all for any options not available to be specified elsewhere.  May be specified multiple times.")
    args = parser.parse_args()

    CV_Test = DataplaneTest(lf_host = args.mgr,
                            lf_port = args.port,
                            lf_user = args.lf_user,
                            lf_password = args.lf_password,
                            instance_name = args.instance_name,
                            config_name = args.config_name,
                            upstream = args.upstream,
                            pull_report = args.pull_report,
                            load_old_cfg = args.load_old_cfg,
                            download_speed = args.download_speed,
                            upload_speed = args.upload_speed,
                            duration = args.duration,
                            dut = args.dut,
                            station = args.station,
                            enables = args.enable,
                            disables = args.disable,
                            raw_lines = args.raw_line,
                            sets = args.set
                            )
    CV_Test.setup()
    CV_Test.run()


if __name__ == "__main__":
    main()
