#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

This script is used to automate running TR398 tests.  You
may need to view a TR398 test configured through the GUI to understand
the options and how best to input data.
    
    ./lf_tr398_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name tr398-instance --config_name test_con \
      --upstream 1.2.eth2 \
      --dut5 'TR398-DUT ruckus750-5 4c:b1:cd:18:e8:ec (1)' \
      --dut2 'TR398-DUT ruckus750-2 4c:b1:cd:18:e8:e8 (2)' \
      --raw_lines_file example-configs/tr398-ferndale-ac-cfg.txt \
      --set 'Calibrate Attenuators' 0 \
      --set 'Receiver Sensitivity' 0 \
      --set 'Maximum Connection' 1 \
      --set 'Maximum Throughput' 1 \
      --set 'Airtime Fairness' 0 \
      --set 'Range Versus Rate' 0 \
      --set 'Spatial Consistency' 0 \
      --set 'Multiple STAs Performance' 0 \
      --set 'Multiple Assoc Stability' 0 \
      --set 'Downlink MU-MIMO' 0 \
      --set 'AP Coexistence' 0 \
      --set 'Long Term Stability' 0

Note:
    --raw_line 'line contents' will add any setting to the test config.  This is
        useful way to support any options not specifically enabled by the
        command options.
    --set modifications will be applied after the other config has happened,
        so it can be used to override any other config.  Above, we are disabling many
        of the subtests, and enablign just Maximum Connection and Maximum Throughput
        tests.

    The RSSI values are calibrated, so you will need to run the calibration step and
    call with appropriate values for your particular testbed.  This is loaded from
    example-configs/tr398-ferndale-ac-cfg.txt in this example.
    Contents of that file is a list of raw lines, for instance:

rssi_0_2-0: -26
rssi_0_2-1: -26
rssi_0_2-2: -26
....

Example of raw text config for TR-398, to show other possible options:

show_events: 1
show_log: 0
port_sorting: 0
kpi_id: TR_398
notes0: Standard LANforge TR-398 automation setup, DUT is in large chamber CT840a, LANforge test system is in
notes1: smaller CT810a chamber.  CT704b and CT714 4-module attenuators are used.  Directional antennas
notes2: mounted on the sides of the DUT chamber are used to communicate to the DUT.   DUT is facing forward at
notes3: the zero-rotation angle.
bg: 0xE0ECF8
test_rig: TR-398 test bed
show_scan: 1
auto_helper: 1
skip_2: 0
skip_5: 0
skip_5b: 1
skip_dual: 0
skip_tri: 1
selected_dut5: TR398-DUT ruckus750-5 4c:b1:cd:18:e8:ec (1)
selected_dut2: TR398-DUT ruckus750-2 4c:b1:cd:18:e8:e8 (2)
upstream_port: 1.2.2 eth2
operator: 
mconn: 5
band2_freq: 2437
band5_freq: 5180
tos: 0
speed: 65%
speed_max_cx_2: 2000000
speed_max_cx_5: 8000000
max_tput_speed_2: 100000000
max_tput_speed_5: 560000000
rxsens_deg_rot: 45
rxsens_pre_steps: 8
stability_udp_dur: 3600
stability_iter: 288
calibrate_mode: 4
calibrate_nss: 1
dur120: 120
dur180: 180
i_5g_80: 195000000
i_5g_40: 90000000
i_2g_20: 32000000
spatial_deg_rot: 30
spatial_retry: 0
reset_pp: 99
rxsens_stop_at_pass: 0
auto_coex: 1
rvr_adj: 0
rssi_2m_2: -20
rssi_2m_5: -32
extra_dl_path_loss: 3
dur60: 60
turn_table: TR-398
radio-0: 1.1.2 wiphy0
radio-1: 1.1.3 wiphy1
radio-2: 1.1.4 wiphy2
radio-3: 1.1.5 wiphy3
radio-4: 1.1.6 wiphy4
radio-5: 1.1.7 wiphy5
rssi_0_2-0: -26
rssi_0_2-1: -26
rssi_0_2-2: -26
rssi_0_2-3: -26
rssi_0_2-4: -27
rssi_0_2-5: -27
rssi_0_2-6: -27
rssi_0_2-7: -27
rssi_0_2-8: -25
rssi_0_2-9: -25
rssi_0_2-10: -25
rssi_0_2-11: -25
rssi_0_5-0: -38
rssi_0_5-1: -38
rssi_0_5-2: -38
rssi_0_5-3: -38
rssi_0_5-4: -38
rssi_0_5-5: -38
rssi_0_5-6: -38
rssi_0_5-7: -38
rssi_0_5-8: -47
rssi_0_5-9: -47
rssi_0_5-10: -47
rssi_0_5-11: -47
atten-0: 1.1.85.0
atten-1: 1.1.85.1
atten-2: 1.1.85.2
atten-3: 1.1.85.3
atten-4: 1.1.1002.0
atten-5: 1.1.1002.1
atten-8: 1.1.1002.2
atten-9: 1.1.1002.3
atten_cal: 1
rxsens: 0
max_cx: 0
max_tput: 0
atf: 0
rvr: 0
spatial: 0
multi_sta: 0
reset: 0
mu_mimo: 0
stability: 0
ap_coex: 0

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
                 instance_name="tr398_instance",
                 config_name="tr398_config",
                 upstream="1.2.eth2",
                 pull_report=False,
                 load_old_cfg=False,
                 raw_lines_file="",
                 dut5="",
                 dut2="",
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
        self.dut5 = dut5
        self.dut2 = dut2
        self.raw_lines_file = raw_lines_file
        self.upstream = upstream
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "TR-398"
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
        cfg_options = []

        # Read in calibration data and whatever else.
        if self.raw_lines_file != "":
            with open(self.raw_lines_file) as fp:
                line = fp.readline()
                while line:
                    cfg_options.append(line)
                    line = fp.readline()
            fp.close()

        for en in self.enables:
            cfg_options.append("%s: 1"%(en[0]))

        for en in self.disables:
            cfg_options.append("%s: 0"%(en[0]))

        for r in self.raw_lines:
            cfg_options.append(r[0])

        # cmd line args take precedence
        if self.upstream != "":
            cfg_options.append("upstream_port: " + self.upstream)
        if self.dut5 != "":
            cfg_options.append("selected_dut5: " + self.dut5)
        if self.dut2 != "":
            cfg_options.append("selected_dut2: " + self.dut2)

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

  ./lf_tr398_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name tr398-instance --config_name test_con \
      --upstream 1.2.eth2 \
      --dut5 'TR398-DUT ruckus750-5 4c:b1:cd:18:e8:ec (1)' \
      --dut2 'TR398-DUT ruckus750-2 4c:b1:cd:18:e8:e8 (2)' \
      --raw_lines_file example-configs/tr398-ferndale-ac-cfg.txt \
      --set 'Calibrate Attenuators' 0 \
      --set 'Receiver Sensitivity' 0 \
      --set 'Maximum Connection' 1 \
      --set 'Maximum Throughput' 1 \
      --set 'Airtime Fairness' 0 \
      --set 'Range Versus Rate' 0 \
      --set 'Spatial Consistency' 0 \
      --set 'Multiple STAs Performance' 0 \
      --set 'Multiple Assoc Stability' 0 \
      --set 'Downlink MU-MIMO' 0 \
      --set 'AP Coexistence' 0 \
      --set 'Long Term Stability' 0

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
    parser.add_argument("-r", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")
    parser.add_argument("--load_old_cfg", default=False, action='store_true',
                        help="Should we first load defaults from previous run of the capacity test?  Default is False")

    parser.add_argument("--dut2", default="",
                        help="Specify 2Ghz DUT used by this test, example: 'TR398-DUT ruckus750-2 4c:b1:cd:18:e8:e8 (2)'")
    parser.add_argument("--dut5", default="",
                        help="Specify 5Ghz DUT used by this test, example: 'TR398-DUT ruckus750-5 4c:b1:cd:18:e8:ec (1)'")

    parser.add_argument("--enable", action='append', nargs=1, default=[],
                        help="Specify options to enable (set value to 1). Example:  --enable show_log  See example raw text config for possible options.  May be specified multiple times.")
    parser.add_argument("--disable", action='append', nargs=1, default=[],
                        help="Specify options to disable (set value to 0).  Example: --disable show_events   See example raw text config for possible options.  May be specified multiple times.")
    parser.add_argument("--set", action='append', nargs=2, default=[],
                        help="Specify options to set values based on their label in the GUI. Example: --set 'IP ToS:' 64  May be specified multiple times.")
    parser.add_argument("--raw_line", action='append', nargs=1, default=[],
                        help="Specify lines of the raw config file.  Example: --raw_line 'pkts: Custom;60;142;256;512;1024;MTU'  See example raw text config for possible options.  This is catch-all for any options not available to be specified elsewhere.  May be specified multiple times.")
    parser.add_argument("--raw_lines_file", default="",
                        help="Specify a file of raw lines to apply.")
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
                            dut2 = args.dut2,
                            dut5 = args.dut5,
                            raw_lines_file = args.raw_lines_file,
                            enables = args.enable,
                            disables = args.disable,
                            raw_lines = args.raw_line,
                            sets = args.set
                            )
    CV_Test.setup()
    CV_Test.run()


if __name__ == "__main__":
    main()
